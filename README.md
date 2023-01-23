# UniSC timetable export
Utilises selenium to export the timetable from UniSC Central to a calendar .ics file.

# Install requirements
```bash
pip install -r requirements.txt
```

# Usage
First create a .env file with your usename and password. See `.env.sample` for an example.

Then run the script with:
```bash
python main.py
```

The program will generate a file called `timetable.ics` in the same directory.