async function getCoordinates(ip) {
    try {
        const response = await fetch(`https://ipwho.is/${ip}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || 'IP lookup failed');
        }

        return {
            ip: data.ip,
            latitude: data.latitude,
            longitude: data.longitude,
            city: data.city,
            region: data.region,
            country: data.country,
        };
    } catch (error) {
        console.error('IP lookup failed:', error);
        return null;
    }
}

async function getForecast(geographic_data) {
    const { latitude, longitude } = geographic_data;
    try {
        const response = await fetch(`https://api.weather.gov/points/${latitude},${longitude}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || 'Unable to Get Forcast URL');
        }
        return data.properties.forecast
    }

    catch (error) {
        console.error('Unable to Get Forcast URL:', error);
        return null;
    }
}

async function getWeatherData(forecast_url) {
    try {
        const response = await fetch(forecast_url);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || 'Unable to Get Forcast URL');
        }
        return data.properties.periods[0]
    }

    catch (error) {
        console.error('Unable to Get Forcast URL:', error);
        return null;
    }
}

async function getWeather(ip) {
    const coordinates = await getCoordinates(ip) 
    const forecast = await getForecast(coordinates)
    const weather = await getWeatherData(forecast)
    const now = new Date();
    const dayLong = now.toLocaleString('default', { weekday: 'long' });
    const date  = String(now.getDate()).padStart(2, '0');

    const cityEl = document.getElementById("weather-city")
    const timeEl = document.getElementById("weather-time")
    const shortForecastEl = document.getElementById("weather-shortForecast")
    const tempEl = document.getElementById("weather-temp")

    cityEl.textContent = `${coordinates.city}, ${coordinates.region}`
    timeEl.textContent = `${dayLong} ${date} ${now.toTimeString()}`
    shortForecastEl.textContent = weather.shortForecast
    tempEl.textContent = weather.temperature
}