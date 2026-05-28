import os

file_path = 'c:/Users/siddharth/Desktop/CardioScanProject/templates/index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Ejection
html = html.replace(
    '<div class="font-mono text-slate-700 text-sm text-blue-600">62.4%</div>',
    '<div id="hud-ejection" class="font-mono text-slate-700 text-sm text-blue-600">62.4%</div>', 1
)

# Replace Rhythm
html = html.replace(
    '<div class="font-mono text-slate-700 text-sm text-blue-600">Sinus</div>',
    '<div id="hud-rhythm" class="font-mono text-slate-700 text-sm text-blue-600">Sinus</div>', 1
)

# Replace Flow
html = html.replace(
    '<div class="font-mono text-slate-700 text-sm text-blue-600">Steady</div>',
    '<div id="hud-flow" class="font-mono text-slate-700 text-sm text-blue-600">Steady</div>', 1
)

# Replace Flux
html = html.replace(
    '<div class="font-mono text-slate-700 text-sm text-blue-600">0.92m/s</div>',
    '<div id="hud-flux" class="font-mono text-slate-700 text-sm text-blue-600">0.92m/s</div>', 1
)

# Replace Sector
html = html.replace(
    '<span class="font-mono text-slate-700 text-[9px] text-blue-600">SECTOR_B7_ISCHEMIC_RISK</span>',
    '<span id="hud-sector" class="font-mono text-slate-700 text-[9px] text-blue-600">SECTOR_B7_ISCHEMIC_RISK</span>', 1
)

# Replace JS logic
js_target = """                      if(data.risk > 50) {
                          $('#resultScore').css('color', '#ffb4ab');
                          $('#resultBar').css('background-color', '#ffb4ab');
                          $('#resultIcon').text('warning').css('color', '#ffb4ab');
                          $('#resultText').text('HIGH RISK ALERT: Ischemic anomalies detected in the neural mapping. Immediate clinical review recommended.');
                      } else {
                          $('#resultScore').css('color', '#8aebff');
                          $('#resultBar').css('background-color', '#8aebff');
                          $('#resultIcon').text('verified').css('color', '#8aebff');
                          $('#resultText').text('LOW RISK: Telemetry indicates optimal cardiovascular function. No significant anomalies detected.');
                      }"""

js_replacement = """                      if(data.risk > 50) {
                          $('#resultScore').css('color', '#ffb4ab');
                          $('#resultBar').css('background-color', '#ffb4ab');
                          $('#resultIcon').text('warning').css('color', '#ffb4ab');
                          $('#resultText').text('HIGH RISK ALERT: Ischemic anomalies detected in the neural mapping. Immediate clinical review recommended.');
                          $('#hud-ejection').text((40 + Math.random() * 9).toFixed(1) + '%').css('color', '#ffb4ab');
                          $('#hud-rhythm').text('Arrhythmia').css('color', '#ffb4ab');
                          $('#hud-flow').text('Restricted').css('color', '#ffb4ab');
                          $('#hud-flux').text((0.3 + Math.random() * 0.2).toFixed(2) + 'm/s').css('color', '#ffb4ab');
                          $('#hud-sector').text('SECTOR_B7_ISCHEMIC_RISK').css('color', '#ffb4ab');
                      } else {
                          $('#resultScore').css('color', '#8aebff');
                          $('#resultBar').css('background-color', '#8aebff');
                          $('#resultIcon').text('verified').css('color', '#8aebff');
                          $('#resultText').text('LOW RISK: Telemetry indicates optimal cardiovascular function. No significant anomalies detected.');
                          $('#hud-ejection').text((55 + Math.random() * 15).toFixed(1) + '%').css('color', '#8aebff');
                          $('#hud-rhythm').text('Sinus').css('color', '#8aebff');
                          $('#hud-flow').text('Steady').css('color', '#8aebff');
                          $('#hud-flux').text((0.8 + Math.random() * 0.4).toFixed(2) + 'm/s').css('color', '#8aebff');
                          $('#hud-sector').text('SECTOR_A1_OPTIMAL').css('color', '#8aebff');
                      }"""

html = html.replace(js_target, js_replacement, 1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Done!')
