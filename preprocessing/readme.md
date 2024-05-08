### CaNeTa MATLAB Code



1. `risk_register_izok_split_semi_colons.m`

   Script to split the IZOK risk register, during the workshop where sticky notes have been separated using semi-colons in the main XLS, this splits based on semi colons to make XLS easier for Ben Seligmann and Steve Micklethwaite to use
   

2. `risk_register_to_boolean.m`

	Script to convert a structured risk register to a Boolean Risk Register for input into the CaNeTA python code initially written by Yifei Lin. Ben Seligman (SMI) knows more about the input file format 
	
	This code works by starting off with the RiskEvents, and breaking data into chunks with a single associated RiskEvent each of these RiskChunks are then processed individually using `process_risk_chunk()`
	
	
	
	`process_risk_chunk.m`
	
	Function that processes a block associated with a single risk chunk. This is done in two parts:
	
	- The first is to iterate through each cause in the chunk:
	  For each cause, the PreventionControls are 'AND'ed together
	- The Second Part is dependent on the presence of MitigationControls:
	  If there are MitigationControls, then `process_mitigation_chunk()` is called
	
	
	
	`process_mitigation_chunk.m`
	
	Function that processes a block associated with a single risk chunk which has mitigation controls present
	
	- For each Consequence:
	  Associated Mitigation controls are 'AND'ed together
