# A software for the conversion of hazard identification data to causal networks for supporting risk management decision making
## Requirements
* Python 3.6 +
  * link path: `C:\Users\USERNAME\AppData\Local\Programs\Python\PythonXX\`
* For windows install add `python -m`/`py -m` before commands
* Install pip: https://www.liquidweb.com/kb/install-pip-windows/
  * `get-pip`
* Install python packages:
  * `pip install -r requirements.txt`
  * `pip install openpyxl`
  * Install pygraphviz: https://pygraphviz.github.io/documentation/stable/install.html 
  * link path for windows: `C:\Program Files (x86)\Graphviz\bin\` 
  * Install Visual C/C++: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  * `pip install graphviz`
  * `pip install --global-option=build_ext --global-option="-IC:\Program Files (x86)\Graphviz\include" --global-option="-LC:\Program Files (x86)\Graphviz\lib" --no-cache-dir pygraphviz` Might be different path, check where the Graphviz file is located.
* Good to go!
## Alternative Installation using Anaconda (Windows)
Install Anaconda: https://www.anaconda.com/products/individual-d

Start `Anaconda Prompt (Anaconda3)`
```
cd <directory where caneta.yml is>
conda env create -f caneta.yml --name caneta
```
Now launch `Spyder (caneta)` from windows start menu
## Alternative Installation No. 2 using Anaconda (Windows and Linux)
This doesn't install as many packages as using the yml approach above, which you may see as a good thing or a bad thing.... Some of the packages installed are probably not strictly required either.

Install Anaconda: https://www.anaconda.com/products/individual-d

Start `Anaconda Prompt (Anaconda3)`
```
conda create -c conda-forge --name caneta-test -y python spyder matplotlib seaborn pandas bokeh networkx pygraphviz graphviz numpy xlsxwriter xlrd scipy scikit-learn jupyter openpyxl pillow pip pyqt statsmodels tqdm
```
Now launch `Spyder (caneta)`
## Usages
* For input format:
  * Please keep the reading network elements inside first three columns.
  * Example format:
  A AND B AND C : (A,B,C) are in a same AND gate. Weight: 3
  A OR B OR C: (A,B,C) are in a same OR gate. Weight: 1
  A AND (B OR C): A is with an AND gate with (B and anther OR gate with C). Weight: 2
  A OR (B AND C): A A is with an OR gate with (B and anther AND gate with C). Weight: 2
* For image:
  * After a new image (.png) file is produced, before next step, please save it into different name or move it to other places.
* For node elimination:
  * After clicking on robustness_topology properties (Degree, InDegree... etc.), network is disappeared. Please import excel file again for further movements.
* Edge Weight:
  * Red : 1, Blue : 2, Green : 3, Yellow : 4, Black : 5, Purple : 6, Grey : 7, Orange : 8, Fuchsia : 9, Olive: 10, Cyan : 11, Brown : 12
## Notes and Acknowledgements
The code is developed using Python written by Yifei Lin `contact: yifei.lin@uq.edu.au`. The project is proposed by Dr Ben Seligmann `contact: b.seligmann@uq.edu.au`, and supervised by Associate Professor Steven Micklethwaite `s.micklethwaite@uq.edu.au`, Dr Ben Seligmann and Dr David Lange `contact: d.lange@uq.edu.au`.
