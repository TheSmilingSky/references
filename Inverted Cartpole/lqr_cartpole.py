from __future__ import division
import cv2
import numpy as np
import math
import time
import matplotlib.pyplot as plt
import sys
import scipy.linalg

def lqr(A,B,Q,R):
	# dx/dt = Ax +Bu
	# cost  = integral x.T*Q*x + u.T*R*u

	# ricatti equation
	X = np.matrix(scipy.linalg.solve_continuous_are(A,B,Q,R))

	# recomputing LQR
	K = np.matrix(scipy.linalg.inv(R)*(B.T*X))

	eigenValues, eigenVectors = scipy.linalg.eig(A - B*K)

	return K, X, eigenValues

class Cart:
	def __init__(self,x,mass,world_size):
		self.x = x
		self.y = int(0.6*world_size)
		self.mass = mass
		self.color = (0,255,0)

class Pendulum:
	def __init__(self,length,theta,ball_mass):
		self.length = length
		self.theta = theta
		self.ball_mass = ball_mass
		self.color = (0,0,255)

def display_stuff(world_size,cart,pendulum):
	length_for_display = pendulum.length * 100
	A = np.zeros((world_size,world_size,3),np.uint8)
	cv2.line(A,(0,int(0.6 * world_size)),(world_size,int(0.6 * world_size)),(255,255,255),2)
	cv2.rectangle(A,(int(cart.x) + 25,cart.y + 15),(int(cart.x) - 25,cart.y - 15),cart.color,-1)	
	pendulum_x_endpoint = int(cart.x - (length_for_display) * math.sin(pendulum.theta))
	pendulum_y_endpoint = int(cart.y - (length_for_display) * math.cos(pendulum.theta))
	cv2.line(A,(int(cart.x),cart.y),(pendulum_x_endpoint,pendulum_y_endpoint),pendulum.color,4)
	cv2.circle(A,(pendulum_x_endpoint,pendulum_y_endpoint),6,(255,255,255),-1)
	cv2.imshow('WindowName',A)
	cv2.waitKey(5)

def find_lqr(cart, pendulum, time_delta, error, previous_error, theta_dot, x_dot, g):
	A = np.matrix(  [
					[0,1,0,0],
					[0,0,g*pendulum.ball_mass/cart.mass,0],
					[0,0,0,1],
					[0,0,(cart.mass+pendulum.ball_mass)*g/(pendulum.length*cart.mass),0]
					])
	
	B = np.matrix(	[
					[0],
					[1/cart.mass],
					[0],
					[1/(pendulum.length*cart.mass)]
					])

	Q = np.matrix(	[
					[10,0,0,0],
					[0,1,0,0],
					[0,0,100,0],
					[0,0,0,1000]
					])

	R = np.matrix([500])

	K, S, E = lqr(A, B, Q, R)
	np.matrix(K)

	x = np.matrix(	[
					[np.squeeze(np.asarray(cart.x))],
					[np.squeeze(np.asarray(x_dot))],
					[np.squeeze(np.asarray(pendulum.theta))],
					[np.squeeze(np.asarray(theta_dot))]
					])

	desired = np.matrix(	[
					[300],
					[0],
					[0],
					[0]
					])

	F = -(K*(x-desired))
	return np.squeeze(np.asarray(F))

def apply_control_input(cart,pendulum,F,time_delta,x_tminus2,theta_dot,theta_tminus2,previous_time_delta,g):
	theta_double_dot = (((cart.mass + pendulum.ball_mass) * g * math.sin(pendulum.theta)) + (F * math.cos(pendulum.theta)) - (pendulum.ball_mass * ((theta_dot)**2.0) * pendulum.length * math.sin(pendulum.theta) * math.cos(pendulum.theta))) / (pendulum.length * (cart.mass + (pendulum.ball_mass * (math.sin(pendulum.theta)**2.0)))) 
	x_double_dot = ((pendulum.ball_mass * g * math.sin(pendulum.theta) * math.cos(pendulum.theta)) - (pendulum.ball_mass * pendulum.length * math.sin(pendulum.theta) * (theta_dot**2)) + (F)) / (cart.mass + (pendulum.ball_mass * (math.sin(pendulum.theta)**2)))
	cart.x += ((time_delta**2) * x_double_dot) + (((cart.x - x_tminus2) * time_delta) / previous_time_delta)
	pendulum.theta += ((time_delta**2)*theta_double_dot) + (((pendulum.theta - theta_tminus2)*time_delta)/previous_time_delta)

def find_error(pendulum):
	previous_error = (pendulum.theta % (2 * math.pi)) - 0
	if previous_error > math.pi:
		previous_error = previous_error - (2 * math.pi)
	return previous_error

def plot_graphs(times,errors,theta,force,x):
	plt.subplot(4, 1, 1)
	plt.plot(times,errors,'-b')
	plt.ylabel('Error')
	plt.xlabel('Time')

	plt.subplot(4, 1, 2)
	plt.plot(times,theta,'-b')
	plt.ylabel('Theta')
	plt.xlabel('Time')

	plt.subplot(4, 1, 3)
	plt.plot(times,force,'-b')
	plt.ylabel('Force')
	plt.xlabel('Time')

	plt.subplot(4, 1, 4)
	plt.plot(times,x,'-b')
	plt.ylabel('X')
	plt.xlabel('Time')

	plt.show()

def main():
	mass_of_ball = 1.0
	mass_of_cart = 5.0
	g = 9.81
	errors, force, theta, times, x = [],[],[],[],[]
	world_size = 700
	simulation_time = 30
	previous_timestamp = time.time()
	end_time = previous_timestamp + simulation_time

	cart = Cart(int(0.2 * world_size),mass_of_cart,world_size)
	pendulum = Pendulum(1,1,mass_of_ball)

	theta_dot = 0
	theta_tminus1 = theta_tminus2 = pendulum.theta
	x_tminus1 = x_tminus2 = cart.x
	previous_error = find_error(pendulum)
	integral = 0
	previous_time_delta = 0
	
	while time.time() <= end_time:		
		current_timestamp = time.time()
		time_delta = (current_timestamp - previous_timestamp)
		error = find_error(pendulum)
		if previous_time_delta != 0:	# This condition is to make sure that theta_dot is not infinity in the first step
			theta_dot = (theta_tminus1 - theta_tminus2 ) / previous_time_delta				
			x_dot = (x_tminus1 - x_tminus2) / previous_time_delta
			F = find_lqr(cart,pendulum,time_delta,error,previous_error,theta_dot,x_dot,g)
			apply_control_input(cart,pendulum,F,time_delta,x_tminus2,theta_dot,theta_tminus2,previous_time_delta,g)
			
			force.append(F)
			x.append(cart.x)
			errors.append(error)		
			times.append(current_timestamp)
			theta.append(pendulum.theta)
	
		display_stuff(world_size,cart,pendulum)
		previous_time_delta = time_delta
		previous_timestamp = current_timestamp
		previous_error = error
		theta_tminus2 = theta_tminus1
		theta_tminus1 = pendulum.theta
		x_tminus2 = x_tminus1
		x_tminus1 = cart.x

	plot_graphs(times,errors,theta,force,x)

if __name__ == "__main__":
	main()
