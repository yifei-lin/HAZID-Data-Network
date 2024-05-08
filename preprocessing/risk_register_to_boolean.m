%% CaNeTA
% Script to convert a structured risk register to a Boolean Risk Register
% for input into the CaNeTA python code initially written by Yifei Lin
% Ben Seligman (SMI) knows more about the input file format
%
% This code works by starting off with the RiskEvents, and breaking
% Data into chunks with a single associated RiskEvent each of these
% RiskChunks are then processed individually

% %% Read in Data
% xls_in = 'C:\Users\uqgforbe\code\development\MATLAB\CaNeTa\FOR GORDON - Put into excel structure for autoboolean creation v3.xlsx';
% xls_out = 'C:\Users\uqgforbe\code\development\MATLAB\CaNeTa\output2.xls';
% xls_out_type = 'C:\Users\uqgforbe\code\development\MATLAB\CaNeTa\output2_type.xls';
%
% clc
% t = readtable(xls_in,...
%     'Sheet','Sheet2',...
%     'Range','D1:H14',...
%     'ReadVariableNames',true);
% t.Properties.VariableNames={'Cause','PreventionControl','RiskEvent','MitigationControl','Consequence'};

%%

xls_in = "R:\CANETARI-Q5024\Data\Mine closure example - made up\Closure example input v1.xlsx";
xls_out = "R:\CANETARI-Q5024\Data\Mine closure example - made up\Boolean.xlsx";
xls_out_type =  "R:\CANETARI-Q5024\Data\Mine closure example - made up\Intermediate.xlsx";
clc
t = readtable(xls_in,...
    'Sheet','CaNeTA Template',...
    'Range','E1:J150',...
    'ReadVariableNames',true);
t = removevars(t,{'AND'});
t.Properties.VariableNames={'Cause','PreventionControl','RiskEvent','MitigationControl','Consequence'};

for v=1:numel(t.Properties.VariableNames)
    vn = t.Properties.VariableNames{v};
    try
        % will fail if column is not numeric...
        if all(isnan(t.(vn)))
            t.(t.Properties.VariableNames{v}) =repmat({''},size(t,1),1);
        end
    catch
    end
end

%% Replace Brackets
warning('off','MATLAB:strrep:InvalidInputType');
for r=1:size(t,1)
    for c=1:size(t,2)
        t{r,c} = strrep(t{r,c},'(','[');
        t{r,c} = strrep(t{r,c},')',']');
    end
end

%% Make table all lowercase
t_lower = cellfun(@(x) lower(x),table2cell(t),'UniformOutput',false);
% convert 'none' to 'None'
% t_lower = cellfun(@(x) strrep(x,'none','None'),t_lower,'UniformOutput',false);
t(1:end,1:end) = t_lower;


%% Get the current risk chunk
risk_start = 1;
risk_end = risk_start;

out_all={};
while risk_end<=size(t,1)
    while risk_end<size(t,1) && isempty(t.RiskEvent{risk_end+1})
        risk_end=risk_end+1;
    end
    risk_chunk = t(risk_start:risk_end,:);

    out = process_risk_chunk(risk_chunk);
    out_all = cat(1,out_all,out);
    % prepare to get next chunk
    risk_start=risk_end+1;
    risk_end=risk_end+1;

end
disp(out_all);

if exist(xls_out,'file')
    delete(xls_out)
    pause(5);
end
xlswrite(xls_out,cat(1,{'Deviation','Possible Causes','Consequences'},out_all));
fprintf('Created: %s\n',xls_out);

%%
node_type = stack(t,1:5);
node_type.Properties.VariableNames={'Type','NodeName'};
idx =cellfun(@isempty,node_type.NodeName);
node_type = node_type(~idx,:);
node_type = node_type(:,{'NodeName' 'Type' });

NodeNames = unique(node_type.NodeName);
node_type_out = {};
for i=1:numel(NodeNames)
    nt = node_type(strcmpi(node_type.NodeName,NodeNames(i)),:);
    nt2 = char(nt.Type);
    nt2 = unique(cellstr(nt2));
    if size(nt2,1)>1
        nt2 = strjoin(nt2,'_');
    else
        nt2=nt2{1};
    end
    node_type_out(end+1,:) = {NodeNames{i} nt2};

end

if exist(xls_out_type,'file')
    delete(xls_out_type);
    pause(5);
end
xlswrite(xls_out_type,node_type_out);
fprintf('Created: %s\n',xls_out_type);
