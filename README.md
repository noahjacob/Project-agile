# Project-agile

## Getting Started

Follow these steps to set up the project locally:

### 1. Clone the repository

```bash
git clone https://github.com/noahjacob/Project-agile.git
cd Project-agile
```

### 2. (Optional) Create and activate a virtual environment

It is recommended to use a virtual environment to manage dependencies separately.

```
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Run the Streamlit app

```
streamlit run weather_dashboard.py
```

## Features

Below are the key features implemented in the Weather Dashboard Web App. Each section includes a short explanation and a demo of the feature in use.

### User Login & Profile Settings

Users can log in using a username or email. Their dashboard settings (such as selected sections or favorite locations) are saved and automatically loaded on future logins.

#### What it does:
- Allows users to log in with just a username or email
- Saves preferences like selected UI sections and favorite cities
- Loads saved preferences automatically on next login

#### Demo:

![User Login Demo](https://github.com/user-attachments/assets/d6a7d695-a636-43e9-b35b-9891567314ef)


### City Search

Users can search for any city to view current weather conditions, detailed information, and forecasts. The app provides real-time feedback for invalid or unavailable locations.

#### What it does:
- Allows users to enter any city to view weather data
- Displays current conditions, graphs, and forecasts for the selected city
- Handles invalid city names with clear error messages

#### Demo:

![City Search Demo](https://github.com/user-attachments/assets/f2a6c9cd-b40b-4c66-a153-c2da7268edb4)


### Temperature Unit Toggle and Graph Duration Control

Users have control over how weather data is displayed on the dashboard, including the choice of temperature units and the duration of data shown in graphs.

#### What it does:
- **Temperature Toggle**: Switch between Celsius and Fahrenheit to view temperature in your preferred unit
- **Graph Duration Control**: Adjust the number of past hours (in 12-hour increments up to 48 hours) displayed for temperature and humidity graphs
- Both settings dynamically update the visuals and enhance user personalization

#### Demo:
![Temp and Graph Demo](https://github.com/user-attachments/assets/4cd380fe-67de-4d4b-9eb4-a4e5832c693c)

### Favorite Locations

Users can save frequently viewed cities as favorites and quickly switch between them. This streamlines access to weather data for multiple locations.

#### What it does:
- Lets users save up to 5 favorite cities
- Provides a dropdown or selection menu to quickly switch between saved locations
- Allows removal of cities from the favorites list
- Persists favorites across sessions for logged-in users

#### Demo:
![Favorite Locations Demo](https://github.com/user-attachments/assets/1b379b00-6f6e-46a0-89eb-e6aa4d7d1ca8)


### Customizable UI Sections

Users can personalize their dashboard by selecting which sections to display, such as current weather, graphs, sunrise/sunset times, and the 7-day forecast.

#### What it does:
- Provides a filter or toggle menu to select visible sections
- Dynamically shows or hides components based on user selection
- Enhances usability by reducing clutter and focusing on relevant data
- Preferences are saved for logged-in users

#### Demo:
![Sections Demo](https://github.com/user-attachments/assets/2aa307f8-e489-480c-a22c-526f095f1f90)


