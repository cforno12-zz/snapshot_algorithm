# "make" for a quick branch
# Then you can do python controller.py...
# to run it if you only want one branch
# for some reason.
# This isn't very useful, you should
# just do what I say in the readme:
#
# python branch.py <name> <port> <time_interval>
# python controller.py <total_money> <filename>

branch : 
	python branch.py branch1 9090 1000
