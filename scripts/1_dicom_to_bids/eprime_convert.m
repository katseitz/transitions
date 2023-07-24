addpath(genpath('~/matlab_repos'))
basedir = '/projects/b1108/studies/transitions2/data/raw/neuroimaging/behavioural';
basedir2 = '/projects/b1108/studies/transitions2/data/raw/neuroimaging/bids';

mid = 1;
chat = 0;
make_plot = 0;
save_output = 0;

if mid == 1
    % ask Zach -- this was pylling the -1.txt file which seems to be empty
    % for a lot of people. 

    %TO-DO: add robust error handing. Some p's are erroring bc they don't 
    %all of the cue values. 
    fnames = filenames(fullfile(basedir,'sub-*/ses-1/beh/3_MID*2.txt'));

    for sub = 1:length(fnames)
        % Load in the text file
        txt = readtable(fnames{sub});
        % changed below bc new file path... will need to modify for foundations 
        pid{sub} =  fnames{sub}(76:80);% CREST (77:82);  Georgia (81:86); RISE (60:64)
        func_dir = fullfile(basedir2,strcat('sub-',pid{sub},'/ses-1/func/'));
        if exist(func_dir, 'dir') == 0
            mkdir(func_dir);
        end
        if isempty(txt) == 0
            
            % get rid of fields that overlap in inconvenient ways. I want to
            % use RunList1/RunList2 later on to figure out which trial everyone
            % is looking at
            txt(find(contains(txt.Var1,'RunList1.Cycle')),:) = [];
            txt(find(contains(txt.Var1,'RunList1.Sample')),:) = [];
            txt(find(contains(txt.Var1,'RunList2.Cycle')),:) = [];
            txt(find(contains(txt.Var1,'RunList2.Sample')),:) = [];

            % create vars for all time points of interest
            % target response
            tgt_on = txt.Var2(find(contains(txt.Var1,'Run1Tgt.OnsetTime')));
            tgt_dur = txt.Var2(find(contains(txt.Var1,'TgtDur')));
            % cue onset and duration
            cue_on1 = txt.Var2(find(contains(txt.Var1,'Run1Cue.OnsetTime')));
            cue_on1 = (cue_on1 - txt.Var2(strcmp(txt.Var1,'Run1Fix.OnsetTime'))) ./ 1000;
            cue_on2 = txt.Var2(find(contains(txt.Var1,'Run2Cue.OnsetTime')));
            cue_on2 = (cue_on2 - txt.Var2(strcmp(txt.Var1,'Run2Fix.OnsetTime'))) ./ 1000;
            if length(cue_on1)==length(cue_on2)
                cue_rt_time = txt.Var2(find(contains(txt.Var1,'Run1Cue.RTTime')));
                cue_dur = txt.Var2(find(contains(txt.Var1,'Run1Cue.Duration')));
                % ITI onset
                cue_iti1 = txt.Var2(find(contains(txt.Var1,'Run1Dly3.OnsetTime')));
                cue_iti1 = (cue_iti1 - txt.Var2(strcmp(txt.Var1,'Run1Fix.OnsetTime'))) ./ 1000;
                trial_duration1 = round(cue_iti1 - cue_on1);
                cue_iti2 = txt.Var2(find(contains(txt.Var1,'Run2Dly3.OnsetTime')));
                cue_iti2 = (cue_iti2 - txt.Var2(strcmp(txt.Var1,'Run1Fix.OnsetTime'))) ./ 1000;
                trial_duration2 = round(cue_iti2 - cue_on2);
    
                % response times of participant responses
                rt1 = txt.Var2(find(contains(txt.Var1,'Run1Tgt.RT')));
                rt1(rt1 == 0) = NaN;
                rt2 = txt.Var2(find(contains(txt.Var1,'Run2Tgt.RT')));
                rt2(rt2 == 0) = NaN;
                % feedback onset and duration
                fbk_on1 = txt.Var2(find(contains(txt.Var1,'Run1Fbk.OnsetTime')));
                fbk_on1 = (fbk_on1 - txt.Var2(strcmp(txt.Var1,'Run1Fix.OnsetTime'))) ./ 1000;
                fbk_on2 = txt.Var2(find(contains(txt.Var1,'Run2Fbk.OnsetTime')));
                fbk_on2 = (fbk_on2 - txt.Var2(strcmp(txt.Var1,'Run1Fix.OnsetTime'))) ./ 1000;
                fbk_dur = txt.Var2(find(contains(txt.Var1,'Run1Fbk.Duration')));
                % Was the participant accurate?
                acc1 = ~isnan(rt1);
                acc2 = ~isnan(rt2);
                rwd = txt.Var2(find(contains(txt.Var1,'Rwd')));
                
                % what was the target rt?
                target_RT1 = txt.Var2(find(contains(txt.Var1,'Run1Tgt.Duration')));
                target_RT2 = txt.Var2(find(contains(txt.Var1,'Run2Tgt.Duration')));
                target_RT1(target_RT1 < 0) = [];
                target_RT2(target_RT2 < 0) = [];
                % I'm adding a '-' so that I can more easily refer to the
                % string below. When I only had a '1', too many replacements
                % were happening lol
    
                trial_type1 = strcat(string(txt.Var2(find(contains(txt.Var1,'RunList1')))),'-');
                trial_type2 = strcat(string(txt.Var2(find(contains(txt.Var1,'RunList2')))),'-');
                
                trial_type1 = replace(trial_type1,'1-','Run1 Win $5.00');
                trial_type1 = replace(trial_type1,'2-','Run1 Win $1.50');
                trial_type1 = replace(trial_type1,'3-','Run1 Win $0.00');
                trial_type1 = replace(trial_type1,'4-','Run1 Lose $5.00');
                trial_type1 = replace(trial_type1,'5-','Run1 Lose $1.50');
                trial_type1 = replace(trial_type1,'6-','Run1 Lose $0.00');
    
                trial_type2 = replace(trial_type2,'1-','Run2 Win $5.00');
                trial_type2 = replace(trial_type2,'2-','Run2 Win $1.50');
                trial_type2 = replace(trial_type2,'3-','Run2 Win $0.00');
                trial_type2 = replace(trial_type2,'4-','Run2 Lose $5.00');
                trial_type2 = replace(trial_type2,'5-','Run2 Lose $1.50');
                trial_type2 = replace(trial_type2,'6-','Run2 Lose $0.00');
                
                % compile final variables to put into table
                all_cue_on = [cue_on1;cue_on2];
                all_cue_dur = cue_dur;
                all_fbk_on = [fbk_on1;fbk_on2];
                all_fbk_dur = fbk_dur;
                all_response_time = [rt1;rt2]; all_response_time(all_response_time==0) = NaN;
                all_trial_type = [trial_type1;trial_type2];
                all_cue_type = strcat(all_trial_type,' Anticipation');
                all_fbk_type = strcat(all_trial_type,' Feeback');
                all_acc = zeros(length(all_response_time),1); all_acc(all_response_time>0) = 1;
                
                % final variables
                onset = [all_cue_on;all_fbk_on]; 
                duration = [all_cue_dur;all_fbk_dur]; 
                trial_type = [all_cue_type;all_fbk_type];
                

            
                final_MID1 = [cue_on1,trial_duration1,rt1,acc1,fbk_on1];
                final_MID1 = array2table(final_MID1);
                final_MID1.Properties.VariableNames = {'onset','duration','response_time','correct','feedback_onset'};
                trial_type1 = table(trial_type1); trial_type1.Properties.VariableNames = {'type'};
                final_MID1 = [final_MID1,trial_type1];

                final_MID2 = [cue_on2,trial_duration2,rt2,acc2,fbk_on2];
                final_MID2 = array2table(final_MID2);
                final_MID2.Properties.VariableNames = {'onset','duration','response_time','correct','feedback_onset'};
                trial_type2 = table(trial_type2); trial_type2.Properties.VariableNames = {'type'};
                final_MID2 = [final_MID2,trial_type2];

                
                curr_filename1 = fullfile(basedir2, strcat('sub-',pid{sub},'/ses-1/func/sub-',pid{sub},'_ses-1_task-MID_run-01_events.txt'));
                curr_filename2 = fullfile(basedir2, strcat('sub-',pid{sub},'/ses-1/func/sub-',pid{sub},'_ses-1_task-MID_run-02_events.txt'));
            else
                fprintf(strcat('Only one run for: ',pid{sub},'\n'))
            end
            rt_avg(sub,1) = nanmean(all_response_time);
            acc(sub,1) = nansum(all_acc) / length(all_acc);
            %target_RTs_all(sub,:) = [target_RT1',target_RT2'];
        else
            fprintf(strcat('No MID data for: ',fnames{sub},'\n'))
            rt_avg(sub,1) = NaN;
            acc(sub,1) = NaN;
            %target_RTs_all(sub,:) = NaN;
        end
    end   
end
    
%    test_list = {'t1065','t1061','t1070','t1068','t1069','t1071','t1073','t1064'};
%        %'f10462','f10452','f10472','f10722','f10782','f10492','f10752','f10792','10502','f10802','f10442'};
%    for sub = 1:length(test_list)
%        if sub == 1
%            test_idx = contains(fnames,test_list{sub});
%        else
%            temp = contains(fnames,test_list{sub});
%            test_idx = test_idx + temp;
%        end
%    end


if make_plot == 1
    test_idx(isnan(rt_avg)) = [];
    acc(isnan(rt_avg)) = [];
    target_RTs_all(isnan(rt_avg),:) = [];
    rt_avg(isnan(rt_avg)) = [];
    figure(); histogram(rt_avg); hold on; xline(rt_avg(logical(test_idx)),'--r')
    figure(); histogram(acc); hold on; xline(acc(logical(test_idx)),'--r')
    figure(); histogram(target_RTs_all(:,1)'); hold on; xline(target_RTs_all(logical(test_idx),1),'--r')

end

