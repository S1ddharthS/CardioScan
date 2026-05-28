function out = predict_heart(inputArray)
    load('heart_ai_model.mat', 'mdl');
    % Convert incoming list to table format
    vars = mdl.PredictorNames;
    inputTable = array2table(inputArray, 'VariableNames', vars);
    [~, scores] = predict(mdl, inputTable);
    
    riskPercent = scores(2) * 100; % Probability of heart disease
    confidence = max(scores) * 100; % Confidence is the probability of the chosen class
    
    out = [riskPercent, confidence];
end