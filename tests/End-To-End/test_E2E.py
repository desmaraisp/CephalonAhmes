# -*- coding: utf-8 -*-
"""
Created on Sat Jan  1 16:06:32 2022

@author: Philippe
"""

import src.Warframe_patchnotes_thief_script as wpts
import src.AhmesConfig as ahc
import pytest

@pytest.mark.E2E
def test_main_loop():
	wpts.main_loop(ahc.env_config["MaxIterations"], ahc.env_config["Iteration_Interval_Time"], ahc.env_config["Get_Posts_From_General_Discussions_Page"], ahc.env_config["Post_To_scrappertest_subreddit"])


