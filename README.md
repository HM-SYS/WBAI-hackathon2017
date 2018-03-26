# Overview

 We modeled that it is focused on "Episodic memory" and "place cell" of the hippocampal function.

### Episodic memory

　Episodic memory is formed from "When, Where, Who, What did", and so on. Episodic memory is the result of processing sensory information. We assumed that episodic memory is a set of feature vectors.
Then, we modeled that it is combine episodic memory with value.

### Place cell

　In the 3rd WBAI hackathon's task, we thought that locational information was important.
Then, we implemented the place cell model using "Slow Feature Analysis(SFA)".


## Module outline

+![image](https://user-images.githubusercontent.com/30830112/37890140-63568ac8-310a-11e8-8f29-12bd28c695ab.png)


## Learning method

 The agent acuired the features (visual, location) from the visual information.
Episodic memory is saved by the combine features (visual, location) with value.
Value propagates back toward to the start at the end of the episode.
Similar episodes are extracted from current features and the past episodic memory.
Decision making was selected for similar episodes using the softmax method.

## Preferences

- OS Ubuntu 14.04
- Unity 5.3.4f1
- Python 2.7.11

### install
install python modules:
```
pip install -r agent/requirements.txt
```

## Quick Start
download data:

```
./fetch.sh
```

Next, run python module as a server.

```
cd agent
python server.py
```
Open environment with Unity and load Scenes/Startup.
Press Start Button. This will take a few minutes for loading caffe model.

## Reference 

+ [RatLab : an easy to use tool for place code simulations](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3725472/) , frontiers in Computational Neuroscience，2013
+ [WBAI HACKATHON 2017 Sample](https://github.com/wbap/hackathon-2017-sample/wiki/Instruction-for-the-Sample-Code)

## License
+ Apache License, Version 2.0
