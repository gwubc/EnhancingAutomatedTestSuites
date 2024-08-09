# Enhancing Automated Test Suites Using LLMs

### ABSTRACT

Property-based testing (PBT) has the potential to detect additional failures in software, but its complexity limits its widespread use in real projects. This study focuses on generating PBT directly from source code and existing tests using large language models. We propose a multi-step pipeline for PBT generation, and evaluate it against three datasets with different levels of complexity. The paper shows that LLM-generated PBTs can identify additional bugs than the given tests. Our work demonstrates the potential to simplify property-based testing by automating PBT generation using large language models.



### Reproducing
##### Installation
Clone the repository:\
```git clone https://github.com/gwubc/EnhancingAutomatedTestSuites.git```

Install dependencies:\
```pip install -r requirements.txt```

Setup Ollama or use cloud provider:\
[https://github.com/ollama/ollama](https://github.com/ollama/ollama)\
Ensure you have the capability to run 70b models, as 7b models are insufficient for writing code.

##### Running the Program

WIP