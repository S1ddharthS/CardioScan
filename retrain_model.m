function results = retrain_model()
    % RETRAIN_MODEL - Retrain the ensemble model on updated heart.csv
    % Called by Flask when new patient data is added (self-learning loop)
    % Returns: [acc_rf, acc_xgb, acc_svm, ensemble_acc, n_records]
    
    fprintf('=== CardioScan Model Retrain (Self-Learning) ===\n');
    
    % Backup existing model
    if isfile('heart_ai_model.mat')
        copyfile('heart_ai_model.mat', 'heart_ai_model_backup.mat');
        fprintf('Previous model backed up.\n');
    end
    
    % Call train_model to retrain
    results = train_model();
    
    fprintf('=== Retrain Complete ===\n');
end
