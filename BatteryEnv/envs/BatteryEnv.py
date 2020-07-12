import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gym
from gym import spaces

class BatteryEnv(gym.Env):
    """Battery optimization environment for OpenAI gym"""
    metadata = {'render.modes': ['human']}
    
    def __init__(self, calculate_reward_func, df):
        super(BatteryEnv, self).__init__()
        
        self.dict_actions = {0:'discharge',1:'charge',2:'wait'}
        self.df = df
        self.charge = 4
        
        #We have only 3 discrete actions (charge,discharge,wait)
        self.action_space = spaces.Discrete(3)
        
        # our observation space is just one float value - our load 
        self.observation_space = spaces.Box(low=self.df['load'].min(), high=self.df['load'].max(), dtype=np.float16)
        
        # custom function to calculate reward
        self.calculate_reward_func = calculate_reward_func 
        
        # reward list for monitoring
        self.reward_list = []
        
        # actual load list for monitoring
        self.actual_load_list = []
        
        # index of current state within current episode
        self.state_idx = 0
                
    
    def step(self, action): 
        """
        Method to execute one action within the environment 
        according to some outer algorithm and return reward - 'reward',
        changed input load (actual load) - 'obs', boolean on whether episode 
        is over - 'done' and info - '{}', which is empty now.
        """
        #mapping integer to action for actual load calculation
        str_action = self.dict_actions[action]
        
        #increase state idx within episode (day)
        self.state_idx+=1  
        
        #calculating our actual load
        if str_action == 'charge' and self.charge < 4:
            obs = self.df['load'][self.state_idx] + 100
        elif str_action == 'discharge' and self.charge > 0:
            obs = self.df['load'][self.state_idx] - 100
        else:
            obs = self.df['load'][self.state_idx]
        
        # appending actual load to list for monitoring and comparison purposes
        self.actual_load_list.append(obs)
        
        # calculate reward from actual signal via inputted custom function
        reward = self.calculate_reward_func(obs,actual_load_list=self.actual_load_list) 
        
        # appending curr reward to list for monitoring and comparison purposes
        self.reward_list.append(reward) 
        
        
        #checking whether our episode (day interval) ends
        if self.df.iloc[self.state_idx,:].weekday != self.df.iloc[self.state_idx-1].weekday: 
            done = True
        else:
            done = False
            
        return obs, reward, done, {}
        
    def reset(self): 
        """
        here we just return the first state of the next episode:
        """
        return self.df.iloc[self.state_idx,:]
    
    
    def render(self, mode='human', close=False):
    # Render the environment to the screen
          print('random_print')