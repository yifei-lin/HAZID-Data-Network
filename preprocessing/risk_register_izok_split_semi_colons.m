%% Script to split the IZOK risk register, where sticky notes have been
% seperated using semi-colons in the main XLS, this splits based on semi
% colons to make XLS easier for Ben Seligmann and Steve Micklethwaite to use

clear all
clc

xls_in = 'R:\CANETARI-Q5024\Data\Docs from Izok\Izok_lake_SHEC final boolean.xlsx';
xls_out = 'R:\CANETARI-Q5024\Data\Docs from Izok\Izok_lake_SHEC final boolean_split.xlsx';

sheet = 'Register';
range = 'A1:V300';
% We know that dubious things happen when we extend the table by simple
% assignment
warning('off','MATLAB:table:RowsAddedExistingVars');

%% Read in XLS
t = readtable(xls_in,'Sheet',sheet,'Range',range);
t_out = table();
wb=waitbar(0);

cols = {'Financial_toMMG_', 'Productivity_PlantThroughput__MMG_', 'Repuation_MMG_', 'Environment_WaterQuantity_Input_', 'Environment_WaterQuality_Discharge_', 'Environment_WaterQuantity_Discharge_', ...
    'Emissions_Quality_discharge_', 'Emission_Quantity_discharge_', 'Conservation_Fauna_e_gCaribou_', 'TailingsAndWasteDumps', 'Social_Safety_Health_WellbeingOfMMGPersonnel', ...
    'Social_Safety_Health_WellbeingOfTransportDrivers'};

for r =1:size(t,1)
    row = t(r,:);
    
    cause = strtrim(split(row.Cause,';'));
    conseq = strtrim(split(row.Consequence_Details_,';'));
    pc = strtrim(split(row.PreventionControl_linkedToRelevantCause_,';'));
    me = strtrim(split(row.MitigationControl_linkedToRelevantConsequence_,';'));
    re = strtrim(split(row.RiskEvent,';'));
    num_rows = max([numel(cause),numel(conseq),numel(pc),numel(me),numel(re)]);
    
    row.OrigRow=0;
    row = movevars(row,'OrigRow','After','SubSystem');
    % start making output structure
    rows_out = row;
    rows_out.RiskID(num_rows)=NaN;
    
    for c=1:num_rows
        rows_out.ProcessingOption(c) = row.ProcessingOption;
        rows_out.SubSystem(c) = row.SubSystem;
        rows_out.OrigRow(c) = r+1;
    end
    
    for c =1 :numel(cause)
        rows_out.Cause{c} = cause{c};
    end
    for c =1 :numel(conseq)
        rows_out.Consequence_Details_{c} = conseq{c};
    end
    for c =1 :numel(pc)
        rows_out.PreventionControl_linkedToRelevantCause_{c} = pc{c};
    end
    for c =1 :numel(me)
        rows_out.MitigationControl_linkedToRelevantConsequence_{c} = me{c};
    end
    for c =1 :numel(re)
        rows_out.RiskEvent{c} = re{c};
    end
    
    for c=1:num_rows
        rows_out.AND(c) = NaN;
        rows_out.RiskID(c) = NaN;
        
        for c2=1:numel(cols)
           rows_out.(cols{c2})(c)=NaN;
        end
           
    end
    
    t_out = cat(1,t_out,rows_out);
    waitbar(r/size(t,1),wb);
    drawnow
end
delete(wb)
drawnow

for r=1:size(t_out,1)
    for c=1:size(t_out,2)
        if iscell(t_out{r,c})
            if numel(t_out{r,c})==1
                v = t_out{r,c}{1};
                if isempty(v)
                    t_out{r,c}={''};
                end
            end
        end
    end
end
writetable(t_out,xls_out);
fprintf('Created: %s\n',xls_out);

