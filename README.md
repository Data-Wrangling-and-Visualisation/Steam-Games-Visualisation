# Steam-Games-Visualisation
This project visualises data of various games from Steam and analyses different trends in them.

## Team:
- **Denis Troegubov (DS-01)**  
  Checkpoint 1:  
  - Scraped and cleaned data from the websites.
  
  Checkpoint 2:  
  - Wrote part of backend and frontend. 
- **Diana Tsoi (DS-02)**  
  Checkpoint 1:  
  - Made Exploratory Data Analysis (EDA) and analyzed trends.

  Checkpoint 2:  
  - Wrote part of backend and frontend.
- **Victor Mazanov (DS-02)**  
  Checkpoint 1:  
  - Made a list of possible trends, scraped data from the websites.  

  Checkpoint 2:  
  - Wrote part of backend and frontend.

## Setup and Run Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Data-Wrangling-and-Visualisation/Steam-Games-Visualisation.git
    cd Steam-Games-Visualisation
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv venv
    ```

3. **Activate the virtual environment:**
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```sh
        source venv/bin/activate
        ```

4. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

### Running the Project

1. **Scrape the data:**
    - Navigate to the [scrape](http://_vscodecontentref_/1) directory:
        ```sh
        cd scrape
        ```
    - Run the Jupyter Notebook to scrape the data:
        ```sh
        jupyter notebook Steam_games_scrape.ipynb
        ```
    - Follow the instructions in the notebook to scrape and save the data to `games.json`.

2. **Navigate to the [eda](http://_vscodecontentref_/2) directory:**
    ```sh
    cd ../eda
    ```

3. **Run the Jupyter Notebook for data analysis:**
    ```sh
    jupyter notebook games.ipynb
    ```

4. **Open the [games.ipynb](http://_vscodecontentref_/3) notebook in your browser and run the cells to visualize the data.**

### Troubleshooting

- If you encounter a `ValueError` related to `nbformat`, ensure you have the correct version installed:
    ```sh
    pip install --upgrade nbformat
    ```

- If you face any issues with missing files, ensure that the `games.json` file is located in the [scrape](http://_vscodecontentref_/4) directory.

5. **Command for project running**

```sh
docker-compose up -d
```