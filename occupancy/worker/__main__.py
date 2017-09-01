from . import scheduler
from . import cleaner

def main():
    cleaner.clean()
    scheduler.start()

if __name__ == '__main__':
    main()
