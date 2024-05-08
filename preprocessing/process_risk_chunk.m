function out = process_risk_chunk(risk_chunk)
% Function that processes a block associated with a single risk chunk
% This is done in two parts:
% The first is to iterate through each cause in the chunk
% For each cause, the PreventionControls are 'AND'ed together
%
% The Second Part is dependent on the presence of MitigationControls
% If there are MitigationControls, then process_mitigation_chunk() is
% called
%
% Otherwise, all the Consequences are 'OR'ed together
cause_start=1;
cause_end=cause_start;
out = '';
while cause_end<=size(risk_chunk,1)
    while cause_end<size(risk_chunk,1) && isempty(risk_chunk.Cause{cause_end+1})
        cause_end=cause_end+1;
    end
    
    if ~isempty(risk_chunk.Cause{cause_start})
        out=sprintf('%s (%s',out,risk_chunk.Cause{cause_start});
        
        for k=cause_start:cause_end
            if ~isempty(risk_chunk.PreventionControl{k})
                out =sprintf('%s AND %s',out,risk_chunk.PreventionControl{k});
            end
        end
        out =sprintf('%s) OR',out);
    else
        fprintf('Warning --- Check This - No Cause!\n');
        disp(risk_chunk)
        out = 'None OR';
    end
    % prepare for next iteration
    cause_start = cause_end+1;
    cause_end=cause_end+1;
    %     fprintf('Cause End: %d\n',cause_end);
end
% remove the trailing OR

if strcmpi(out,' () OR')
    out = 'None OR';
end
% if all(cellfun(@isempty,risk_chunk.MitigationControl))
%     % No Mitigation conrols
%     out2='';
%     for k=1:size(risk_chunk,1)
%         if ~isempty(risk_chunk.Consequence{k})
%             out2 = sprintf('%s %s OR',out2,risk_chunk.Consequence{k});
%         end
%     end
%     % remove trailing or
%     out2 = out2(1:end-3);
%     out = {strtrim(risk_chunk.RiskEvent{1}) strtrim(out(1:end-3)) strtrim(out2)};
% else
out = {strtrim(risk_chunk.RiskEvent{1}) strtrim(out(1:end-3)) 'None'};
out2 = process_mitigation_chunk(risk_chunk(:,3:end));
out = cat(1,out,out2);
% end