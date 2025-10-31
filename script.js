// WeatherNow v5 - warm animated theme
const geocodeBase = "https://geocoding-api.open-meteo.com/v1/search?name=";
const weatherBase = "https://api.open-meteo.com/v1/forecast?timezone=auto&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&forecast_days=10";

let chart;

function showLoader(on=true){ document.getElementById('loader').style.display = on ? 'block' : 'none'; }
function setStatus(msg){ document.getElementById('status').textContent = msg; }

function searchCity(){
  const q = document.getElementById('cityInput').value.trim();
  if(!q){ setStatus('Please enter a city name.'); return; }
  setStatus('Searching...'); showLoader(true);
  fetch(geocodeBase + encodeURIComponent(q))
    .then(r=>r.json())
    .then(data=>{
      if(!data.results || data.results.length===0){ setStatus('City not found.'); showLoader(false); return; }
      const place = data.results[0];
      updateAll(place.latitude, place.longitude, place.name + (place.country?(', '+place.country):''));
    }).catch(e=>{ setStatus('Error searching city.'); showLoader(false); });
}

function detectLocation(){
  if(!navigator.geolocation){ setStatus('Geolocation not supported.'); return; }
  setStatus('Detecting location...'); showLoader(true);
  navigator.geolocation.getCurrentPosition(pos=>{
    updateAll(pos.coords.latitude, pos.coords.longitude, 'Your location');
  }, err=>{ setStatus('Location permission denied.'); showLoader(false); }, {timeout:10000});
}

function updateAll(lat, lon, label){
  setStatus('Fetching weather...'); showLoader(true);
  document.getElementById('radarFrame').src = `https://embed.windy.com/embed2.html?lat=${lat}&lon=${lon}&zoom=6&level=surface&overlay=rain`;
  fetch(`${weatherBase}&latitude=${lat}&longitude=${lon}&current_weather=true`)
    .then(r=>r.json())
    .then(data=>{
      showLoader(false); setStatus('');
      document.getElementById('placeLabel').textContent = label;
      if(data.current_weather) document.getElementById('output').innerHTML = `🌡️ Current: ${data.current_weather.temperature}°C — 💨 ${data.current_weather.windspeed} m/s`;
      else document.getElementById('output').innerHTML = 'No current data';
      if(data.daily && data.daily.time){
        const labels = data.daily.time.map(t=> new Date(t).toLocaleDateString(undefined,{month:'short',day:'numeric'}));
        const tmax = data.daily.temperature_2m_max;
        const tmin = data.daily.temperature_2m_min;
        renderChart(labels, tmax, tmin);
      }
    }).catch(e=>{ showLoader(false); setStatus('Error fetching weather.'); });
}

function renderChart(labels, tmax, tmin){
  const ctx = document.getElementById('forecastChart').getContext('2d');
  if(chart) chart.destroy();
  chart = new Chart(ctx, {
    type:'line',
    data:{ labels, datasets:[ {label:'Max °C',data:tmax,tension:0.3,borderColor:'#ff7a18',backgroundColor:'rgba(255,122,24,0.08)',fill:true},{label:'Min °C',data:tmin,tension:0.3,borderColor:'#ffb199',backgroundColor:'rgba(255,177,153,0.06)',fill:true} ] },
    options:{ responsive:true, plugins:{legend:{position:'top'}}, scales:{ y:{ title:{display:true,text:'Temperature (°C)'} } } }
  });
}

// initialize small demo chart placeholder
document.addEventListener('DOMContentLoaded', ()=>{
  const ctx = document.getElementById('forecastChart').getContext('2d');
  chart = new Chart(ctx,{type:'line',data:{labels:['Day 1','Day 2','Day 3'],datasets:[{label:'Max °C',data:[28,30,27],borderColor:'#ff7a18',fill:false}]},options:{responsive:true}});
});
