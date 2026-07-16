% evaluate_and_plot.m
% Generates comprehensive evaluation graphs for the trained models without changing existing code.

fprintf('Loading dataset and trained models...\n');
data = readtable('heart.csv');
load('heart_ai_model.mat', 'mdl_rf', 'mdl_xgb', 'mdl_svm', 'predictorNames');

X = data(:, predictorNames);
Y_true = categorical(data.target);

fprintf('Predicting using Random Forest...\n');
Y_pred_rf = predict(mdl_rf, X);

fprintf('Predicting using XGBoost...\n');
Y_pred_xgb = predict(mdl_xgb, X);

fprintf('Predicting using SVM...\n');
Y_pred_svm = predict(mdl_svm, X);

% Create Ensemble Predictions (Majority Vote)
vote_rf = str2double(string(Y_pred_rf));
vote_xgb = str2double(string(Y_pred_xgb));
vote_svm = str2double(string(Y_pred_svm));

vote_high_rf = 1 - vote_rf;
vote_high_xgb = 1 - vote_xgb;
vote_high_svm = 1 - vote_svm;

total_high = vote_high_rf + vote_high_xgb + vote_high_svm;
Y_pred_ensemble = categorical(1 - (total_high >= 2)); % Convert back to 0/1 labels

fprintf('Generating plots...\n');
f = figure('Name', 'Comprehensive Model Evaluation', 'NumberTitle', 'off', 'Position', [100, 100, 1200, 800]);

% Confusion Matrix - RF
subplot(2, 2, 1);
cm_rf = confusionchart(Y_true, Y_pred_rf);
cm_rf.Title = 'Random Forest Confusion Matrix';
cm_rf.RowSummary = 'row-normalized';
cm_rf.ColumnSummary = 'column-normalized';

% Confusion Matrix - XGB
subplot(2, 2, 2);
cm_xgb = confusionchart(Y_true, Y_pred_xgb);
cm_xgb.Title = 'XGBoost Confusion Matrix';
cm_xgb.RowSummary = 'row-normalized';
cm_xgb.ColumnSummary = 'column-normalized';

% Confusion Matrix - SVM
subplot(2, 2, 3);
cm_svm = confusionchart(Y_true, Y_pred_svm);
cm_svm.Title = 'SVM Confusion Matrix';
cm_svm.RowSummary = 'row-normalized';
cm_svm.ColumnSummary = 'column-normalized';

% Confusion Matrix - Ensemble
subplot(2, 2, 4);
cm_ens = confusionchart(Y_true, Y_pred_ensemble);
cm_ens.Title = 'Ensemble (Majority Vote) Confusion Matrix';
cm_ens.RowSummary = 'row-normalized';
cm_ens.ColumnSummary = 'column-normalized';

drawnow;
saveas(f, 'comprehensive_evaluation.png');

fprintf('Plots saved to comprehensive_evaluation.png\n');

% Only close the figure if running headless (Python Engine)
if ~usejava('desktop')
    close(f);
end
