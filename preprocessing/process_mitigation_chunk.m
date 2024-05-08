function out2 = process_mitigation_chunk(mitigation_chunk)

% Function that processes a block associated with a single risk chunk which
% has mitigation controls present
%
% For each Consequence:
% Associated Mitigation controls are 'AND'ed together

consequence_start=1;
consequence_end=consequence_start;

out2={};
while consequence_end<=size(mitigation_chunk,1)
    while consequence_end<size(mitigation_chunk,1) && isempty(mitigation_chunk.Consequence{consequence_end+1})
        consequence_end=consequence_end+1;
    end
    
    out=sprintf('(%s',mitigation_chunk.RiskEvent{1});
    consequence_exists=false;
    for k=consequence_start:consequence_end
        if ~isempty(mitigation_chunk.MitigationControl{k})
            out =sprintf('%s AND %s',out,mitigation_chunk.MitigationControl{k});
            consequence_exists=true;
        else
            g=1;
        end
    end
%     if consequence_exists
        out =sprintf('%s)',out);
        mitig = strtrim(mitigation_chunk.Consequence{consequence_start});
        if isempty(mitig)
            mitig = 'None';
        end
        out2 = cat(1,out2,{ strtrim(out) 'None' mitig});
%     end
    % prepare for next iteration
    consequence_start = consequence_end+1;
    consequence_end=consequence_end+1;
    %     fprintf('Cause End: %d\n',cause_end);
end
