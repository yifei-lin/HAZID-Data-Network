# A software for the conversion of hazard identification data to causal networks for supporting risk management decision making
## Requirements
* Python 3.6
* Install python packages:
  * pip install -r requirements.txt
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
* For Adjacency_matrix saving:
  * Please save the matrix in this format: XXXX.csv. Then open it with Microsoft Excel.
## Notes and Acknowledgements
The code is developed using Python and the idea comes from 
