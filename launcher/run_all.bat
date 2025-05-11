@echo off
echo === Twitter Scraper - All Processes Launcher ===
echo.
echo This script will run all scraping processes in sequence.
echo.

echo [1/4] Running keyword search...
python ../scrape/search_tweets.py
echo.

echo [2/4] Fetching profiles...
python ../scrape/fetch_profiles.py
echo.

echo [3/4] Generating DM templates...
python ../dm/generate_dm_template.py
echo.

echo [4/4] Ready to launch DM interactive sender.
echo.
echo Press any key to start sending DMs (manual operation required)
pause > nul
python ../dm/dm_interactive_launcher.py
echo.

echo === All processes completed ===
echo.
echo Press any key to exit...
pause > nul