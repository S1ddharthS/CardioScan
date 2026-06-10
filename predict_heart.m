function out = predict_heart(inputArray)
    % PREDICT_HEART - Predict cardiovascular risk using ensemble architecture
    % Returns: [riskPercent, confidence, rf_vote, xgb_vote, svm_vote, 
    %           imp1..imp13, deviation1..deviation13]
    % Total output: 5 + 13 + 13 = 31 values
    
    load('heart_ai_model.mat', 'mdl_rf', 'mdl_xgb', 'mdl_svm', ...
        'feature_importance', 'predictorNames', 'healthy_means');
    
    inputTable = array2table(inputArray, 'VariableNames', predictorNames);
    
    % Get predictions from all three models
    [label_rf, scores_rf] = predict(mdl_rf, inputTable);
    [label_xgb, scores_xgb] = predict(mdl_xgb, inputTable);
    label_svm = predict(mdl_svm, inputTable);
    
    % Convert labels to numeric votes (0 or 1)
    v_rf = str2double(char(label_rf));
    v_xgb = str2double(char(label_xgb));
    v_svm = str2double(char(label_svm));
    
    % In this dataset: 0 = Disease (High Risk), 1 = Healthy (Low Risk)
    % Convert to High Risk votes (1 = High Risk, 0 = Low Risk) for math
    vote_rf_high = 1 - v_rf;
    vote_xgb_high = 1 - v_xgb;
    vote_svm_high = 1 - v_svm;
    
    % Majority Voting (Stacking) for High Risk
    total_high_votes = vote_rf_high + vote_xgb_high + vote_svm_high;
    
    % Average probability for Class '0' (High Risk)
    % scores(:,1) is the score for the first class ('0')
    prob_rf = scores_rf(1) * 100;
    prob_xgb = (1 / (1 + exp(-scores_xgb(1)))) * 100;
    avg_prob = (prob_rf + prob_xgb) / 2;
    
    if total_high_votes >= 2
        riskPercent = max(51.0, avg_prob);
    else
        riskPercent = min(49.0, avg_prob);
    end
    
    % Confidence is based on unanimity
    if total_high_votes == 3 || total_high_votes == 0
        confidence = 96.5;
    else
        confidence = 66.6;
    end
    
    % Compute per-biomarker deviation from healthy means
    deviations = zeros(1, 13);
    for i = 1:13
        val = inputArray(i);
        healthy = healthy_means(i);
        if healthy ~= 0
            deviations(i) = (val - healthy) / abs(healthy);
        else
            deviations(i) = val;
        end
    end
    
    % Output: [risk, conf, rf_high, xgb_high, svm_high, imp(1:13), dev(1:13)]
    out = [riskPercent, confidence, vote_rf_high, vote_xgb_high, vote_svm_high, ...
           feature_importance, deviations];
end