# -*- coding: utf-8 -*-
"""
Created on Jan 10 18:58:34 2023

@author: Capocchi L.
"""

#Import necessary libraries
import streamlit as st
import pandas as pd
import glob

import os
import subprocess

# Adding an appropriate title for the test website
st.title("Analysing DEVSimPy Yaml File")

st.markdown("This little app analyse a yaml devsimpy file into a web interface. Play around with the various inputs belows using different yaml!")

st.sidebar.markdown("Select sample yaml file if you'd like to use one of the preloaded files.")
_radio = st.sidebar.radio("",("Use Sample Yaml", "Use User Yaml"))

sample_yamls = glob.glob('*.yaml')
samp_yamls_df = pd.DataFrame(sample_yamls,columns=['YAML'])
samp_yaml = st.sidebar.selectbox('Choose a yaml file', samp_yamls_df['YAML'])

#Load image 
user_data = st.sidebar.file_uploader(label="Upload your own yaml")
if _radio == "Use Sample Yaml":
    yaml2load = samp_yaml
elif _radio == "Use User Yaml": 
    yaml2load = user_data


tab1, tab2, tab3 = st.tabs(["Inputs", "Outputs","Content"])

def updateArgs(model,arg):
    
    updated_val = st.session_state[f"{model}.{arg}"]

    cmd = "python devsimpy-nogui.py %s -blockargs %s -updateblockargs \"\"\"{'%s':%s}\"\"\""%(yaml2load,model,arg,str(updated_val))
    if eval(os.popen(cmd).read().replace('true','True'))["success"]:
        st.success("Yaml file updated")
    else:
        st.error("Error during the update of the Yaml file")

with tab1:
    #st.header("Inputs")
    cmd_with_options = ["python","devsimpy-nogui.py",yaml2load,"-blockslist"]
    output = subprocess.run(cmd_with_options,capture_output=True)
    
    for model in eval(output.stdout.decode("utf-8")):
        with st.expander(model):
            cmd_with_options = ["python","devsimpy-nogui.py",yaml2load,"-blockargs", model]
            output = subprocess.run(cmd_with_options,capture_output=True)

            for k,v in eval(output.stdout.decode("utf-8").replace('true','True')).items():
                if type(v) == str:
                    st.text_input(k, v,key=f"{model}.{k}", on_change=updateArgs, args=(model,k,))
                elif type(v) in (int,float):
                    st.text_input(k, v,key=f"{model}.{k}", on_change=updateArgs, args=(model,k,))
                elif type(v) == list:
                    st.multiselect(k,v,[v[0]],key=f"{model}.{k}", on_change=updateArgs, args=(model,k,))
                elif type(v) == bool:
                    st.radio(k,(v,not v),key=f"{model}.{k}", on_change=updateArgs, args=(model,k,))

            #expander.write("""
            #    The chart above shows some numbers I picked for you.
            #    I rolled actual dice for these, so they're *guaranteed* to
            #    be random.""")

with tab3:
    st.header("Textual Content")
    cmd_with_options = ["python","devsimpy-nogui.py",yaml2load,"-json"]
    output = subprocess.run(cmd_with_options,capture_output=True)
    st.json(output.stdout.decode("utf-8"))

#subprocess.run(['ls', '-l'])
