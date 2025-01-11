#!/usr/bin/python3

####################################################################################
#
#  Copyright (c) 2023-2025 Piotr Jochymek
#
#  MIT License
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
####################################################################################

from locale import getlocale

class LANGUAGES:
    lang_id='en'

    STR_DICT={
        "File":{
                "pl":"Plik"},
        "Help":{
                "pl":"Pomoc"},
        "About":{
                "pl":"O programie"},
        "License":{
                "pl":"Licencja"},
        "Open current Log":{
                "pl":"Otwórz log"},
        "Open logs directory":{
                "pl":"Otwórz katalog z logami"},
        "Open homepage":{
                "pl":"Otwórz stronę domową"},
        'New Record ...':{
                "pl":"Nowy Rekord ..."},
        "Import Record ...":{
                "pl":"Importuj rekord ..."},
        'Import "Where Is It?" xml ...':{
                "pl":'Importuj xml z "Where Is It?" ...'},
        'Find ...':{
                "pl":'Szukaj'},
        'Settings ...':{
                "pl":'Ustawienia'},
        'Clear Search Results':{
                "pl":'Wyczyść wyniki wyszukiwania'},
        'Exit':{
                "pl":'Zamknij'},
        'Go to next record':{
                "pl":'Idź do następnego rekordu'},
        'Go to previous record':{
                "pl":'Idź do poprzedniego rekordu'},
        'Go to first record':{
                "pl":'Idź pierwszego rekordu'},
        'Go to last record':{
                "pl":'Idź ostatniego rekordu'},
        'Export record ...':{
                "pl":'Eksportuj rekord'},
        'Rename / Repack ...':{
                "pl":'Zmień nazwę / Przepakuj ...'},
        'Record Info ...':{
                "pl":'Informacje o rekordzie ...'},
        'Delete record ...':{
                "pl":'Skasuj rekord ...'},
        'New group ...':{
                "pl":'Nowa grupa ...'},
        'Remove group ...':{
                "pl":'Usuń grupę ...'},
        'Assign record to group ...':{
                "pl":'Przypisz rekord do grupy ...'},
        'Remove record from group ...':{
                "pl":'Usuń rekord z grupy ...'},
        'Rename / Alias name ...':{
                "pl":'Zmień nazwe / Utwórz alias ...'},
        'Show Custom Data ...':{
                "pl":'Pokaż Dane Użytkownika ...'},
        'Copy full path':{
                "pl":'Kopiuj pełną ścieżkę'},
        'Find next':{
                "pl":'Znajdź następny'},
        'Find prev':{
                "pl":'Znajdź poprzedni'},
        'Unload record data':{
                "pl":'Odładuj dane rekordu'},
        'Search in all records':{
                "pl":'Szukaj we wszystkich rekordach'},
        'All records in repository':{
                "pl":'Wszystkie rekordy w repozytoprium'},
        'All records':{
                "pl":'Wszystkie rekordy'},
        'Path elements':{
                "pl":'Elementy Ścieżki'},
        "Don't use this criterion":{
                "pl":'Nie używaj tego kryterium'},
        "By regular expression":{
                "pl":'Poprzez wyrażenie regularne'},
        "By glob pattern":{
                "pl":'Poprzez wyrażenie "glob"'},
        "By fuzzy match":{
                "pl":'Poprzez dopasowanie rozmyte'},
        'File size':{
                "pl":'Wielkość pliku'},
        'File last modification time':{
                "pl":'Ostatni czas modyfikacji pliku'},
        'Search':{
                "pl":'Szukaj'},
        'Search results':{
                "pl":'Wyniki wyszukiwania'},
        'Show results':{
                "pl":'Pokaż wyniki'},
        'Save results':{
                "pl":'Zapisz wyniki'},
        'Close':{
                "pl":'Zamknij'},
        'Continue search':{
                "pl":'Kontynuuj wyszukiwanie'},
        'New group':{
                "pl":'Nowa grupa'},
        'New group name:':{
                "pl":'Nazwa nowej grupy'},
        'No search results\nClick to open find dialog.':{
                "pl":'Brak wyników wyszukiwania\nKliknij by otworzyć dialog wyszukiwania.'},
        'Name':{
                "pl":'Nazwa'},
        'Size':{
                "pl":'Wielkość'},
        'Time':{
                "pl":'Czas'},
        'Abort loading.':{
                "pl":'Przerwij ładowanie'},
        'Abort':{
                "pl":'Przerwij'},
        'Checking records to load ...':{
                "pl":'Sprawdzanie rekordu do załadowania ...'},
        'Loading records ...':{
                "pl":'Ładowanie rekordów ...'},
        'Records space:':{
                "pl":'Zajętość rekordów:'},
        'Records number:':{
                "pl":'Ilość rekordów:'},
        'Loading records':{
                "pl":'Ładowanie rekordów:'},
        'Records loading aborted':{
                "pl":'Ładowanie rekordów przerwane'},
        'Restart Librer to gain full access to the recordset.':{
                "pl":'Uruchom ponownie Librera by uzyskać pełny dostęp do rekordów.'},
        'Loading errors':{
                "pl":'Błędy ładowania:'},
        'Ready':{
                "pl":'Gotowy'},
        'Path does not exist':{
                "pl":'Ścieżka nie istnieje'},
        'Abort pressed ...':{
                "pl":'Użyto "Przerwij" ... '},
        'Creating dialog ...':{
                "pl":'Tworzenie dialogu" ... '},
        'Internal Label of the record to be created':{
                "pl":'Wewnętrzny identyfikator rekordu do utworzenia'},
        'Path:':{
                "pl":'Ścieżka:'},
        'Path to scan':{
                "pl":'Ścieżka do skanowania:'},
        'Set path to scan.':{
                "pl":'Ustaw ścieżkę do skanowania.'},
        'Select device to scan.':{
                "pl":'Wybierz ścieżkę do skanowania.'},
        'Scan':{
                "pl":'Skanuj'},
        'Start scanning.\n\nIf any Custom Data Extractor is enabled it will be executed\nwith every file that meets its criteria (mask & size).':{
                "pl":'Rozpocznij skanowanie.\n\nJeśli włączony jest dowolny Ekstraktor Danych, zostanie on uruchomiony\nz każdym plikiem spełniającym jego kryteria (maska ​​i rozmiar)'},
        'Cancel':{
                "pl":'Anuluj'},
        'Compression:':{
                "pl":'Kompresja:'},
        'Data record internal compression. A higher value\nmeans a smaller file and longer compression time.\nvalues above 20 may result in extremely long compression\nand memory consumption. The default value is 9.':{
                "pl":'Kompresja wewnętrzna rekordu danych. Wyższa wartość\noznacza mniejszy plik i dłuższy czas kompresji.\nWartości powyżej 20 mogą skutkować ekstremalnie długą kompresją\n i zużyciem pamięci. Wartość domyślna to 9.'},
        'CDE Threads:':{
                "pl":'Wątki CDE:'},
        'Number of threads used to extract Custom Data\n\n0 - all available CPU cores\n1 - single thread (default value)\n\nThe optimal value depends on the CPU cores performace,\nIO subsystem performance and Custom Data Extractor specifics.\n\nConsider limitations of parallel CDE execution e.g.\nnumber of licenses of used software,\nused working directory, needed memory etc.':{
                "pl":'Liczba wątków użytych do wyodrębnienia danych niestandardowych\n\n0 - wszystkie dostępne rdzenie procesora\n1 - pojedynczy wątek (wartość domyślna)\n\nWartość optymalna zależy od wydajności rdzeni procesora,\nwydajności podsystemu wejścia/wyjścia i specyfiki programu Custom Data Extractor.\n\nNależy wziąć pod uwagę ograniczenia równoległego wykonywania CDE, np.\nliczbę licencji używanego oprogramowania,\nużywany katalog roboczy, potrzebną pamięć itp.'},
        'one device mode':{
                "pl":'tryb pojedynczego urządzenia'},
        "Don't cross device boundaries (mount points, bindings etc.) - recommended":{
                "pl":"Nie przekraczaj granic urządzeń (punktów montowania, powiązań itp.) - zalecane"},
        'Custom Data Extractors:':{
                "pl":'Ekstraktory Danych Użytkownika:'},
        '% File cryteria':{
                "pl":'Kryteria plików %'},
        'Custom Data extractor command':{
                "pl":'Kryteria plików %'},
        'File Mask':{
                "pl":'Maska Plików'},
        'Executable':{
                "pl":'Plik wykonywalny'},
        'Parameters':{
                "pl":'Parametry'},
        'UP_TOOLTIP':{
                "en":"Use the arrow to change the order\nin which CDE criteria are checked.\n\nIf a file meets several CDE criteria\n(mask & size), the one with higher priority\nwill be executed. In this table, the first\none from the top has the highest priority,\nthe next ones have lower and lower priority.",
                "pl":"Użyj strzałki, aby zmienić kolejność\nsprawdzania kryteriów CDE.\n\nJeśli plik spełnia kilka kryteriów CDE\n(maska ​​i rozmiar), ten o wyższym priorytecie\nzostanie wykonany. W tej tabeli pierwszy\nplik od góry ma najwyższy priorytet,\nkolejne mają coraz niższy priorytet."},
        "Mark to use CD Extractor":{
                "pl":"Zaznacz by użyć CD ekstraktora"},
        'MASK_TOOLTIP':{
                "en":"Glob expresions separated by comma (',')\ne.g.: '*.7z, *.zip, *.gz'\n\nthe given executable will run\nwith every file matching the expression\n(and size citeria if provided)",
                "pl":"Wyrażenia globalne rozdzielone przecinkiem (',')\nnp.: '*.7z, *.zip, *.gz'\n\nPodany plik wykonywalny zostanie uruchomiony\nz każdym plikiem pasującym do wyrażenia\n(i kryteriów rozmiaru, jeśli zostały podane)"},
        'SIZE_TOOLTIP':{
                "en":'Integer value [in bytes] or integer with unit.\nLeave the value blank to ignore this criterion.\n\nexamples:\n399\n100B\n125kB\n10MB',
                "pl":'Wartość całkowita [w bajtach] lub liczba całkowita z jednostką.\nPozostaw wartość pustą, aby zignorować to kryterium.\n\nPrzykłady:\n399\n100B\n125kB\n10MB'},
        'Maximum file size':{
                "pl":'Maksymalna wielkość pliku'},
        'Minimum file size.':{
                "pl":'minimalna wielkość pliku'},
        'EXEC_TOOLTIP':{
                "en":"Binary executable, batch script, or entire command\n(depending on the 'shell' option setting)\nthat will run with the full path to the scanned file.\nThe executable may have a full path, be located in a PATH\nenvironment variable, or be interpreted by the system shell\n\ncheck 'shell' option tooltip.",
                "pl":'Plik wykonywalny binarny, skrypt wsadowy lub całe polecenie\n(w zależności od ustawienia opcji "shell")\nktóre zostanie uruchomione z pełną ścieżką do skanowanego pliku.\nPlik wykonywalny może mieć pełną ścieżkę, znajdować się w zmiennej środowiskowej PATH\nlub być interpretowany przez powłokę systemową\n\nSprawdź podpowiedź opcji "shell".'},
        'PARS_TOOLTIP':{
                "en":"The executable will run with the full path to the file to extract as a parameter.\nIf other constant parameters are necessary, they should be placed here\nand the scanned file should be indicated with the '%' sign.\nThe absence of the '%' sign means that the file will be passed as the last parameter.\ne.g.:const_param % other_const_param",
                "pl":"Plik wykonywalny zostanie uruchomiony z pełną ścieżką do pliku do wyodrębnienia jako parametrem.\nJeśli wymagane są inne stałe parametry, należy je umieścić tutaj\na skanowany plik należy oznaczyć znakiem '%'.\nBrak znaku '%' oznacza, że ​​plik zostanie przekazany jako ostatni parametr.\ne.g.:const_param % other_const_param"},
        'SHELL_TOOLTIP':{
                "en":"Execute in the system shell.\n\nWhen enabled\nCommand with parameters will be passed\nto the system shell as single string\nThe use of pipes, redirection etc. is allowed.\nUsing of quotes (\") may be necessary. Scanned\nfiles will be automatically enclosed with quotation marks.\nExample:\n{shell_example}\n\nWhen disabled\nAn executable file must be specified,\nthe contents of the parameters field will be\nsplitted and passed as a parameters list.\n\nIn more complicated cases\nit is recommended to prepare a dedicated shell\nscript and use it as a shell command.",
                "pl":"Wykonaj w powłoce systemowej.\n\nPo włączeniu\nPolecenie z parametrami zostanie przekazane\ndo powłoki systemowej jako pojedynczy ciąg\nDozwolone jest używanie potoków, przekierowań itp.\nMoże być konieczne użycie cudzysłowów (\"). Przeskanowane\npliki zostaną automatycznie ujęte w cudzysłowy.\nPrzykład:\n{shell_example}\n\nPo wyłączeniu\nNależy określić plik wykonywalny,\nzawartość pola parametrów zostanie\npodzielona i przekazana jako lista parametrów.\n\nW bardziej skomplikowanych przypadkach\nzaleca się przygotowanie dedykowanego skryptu powłoki i użycie go jako polecenia powłoki."},
        'OPEN_TOOLTIP':{
                "en":"Choose the executable file to serve as a custom data extractor...",
                "pl":"Wybierz plik wykonywalny, który będzie służył jako ekstraktor Danych Użytkownika..."},
        'TIMEOUT_TOOLTIP':{
                "en":"Timeout limit in seconds for single CD extraction.\nAfter timeout executed process will be terminated\n\n'0' or empty field means no timeout.",
                "pl":"Limit czasu w sekundach dla pojedynczej ekstrakcji CD.\nPo przekroczeniu limitu czasu wykonywany proces zostanie zakończony\n\n'0' lub puste pole oznacza brak limitu czasu."},
        'TEST_TOOLTIP_COMMOMN':{
                "en":"Before you run scan, and therefore run your CDE on all\nfiles that will match on the scan path,\ntest your Custom Data Extractor\non a single, manually selected file.\nCheck if it's getting the expected data\nand has no unexpected side-effects.",
                "pl":"Zanim uruchomisz skanowanie, a zatem uruchomisz CDE na wszystkich\nplikach, które będą pasować do ścieżki skanowania,\nprzetestuj swój niestandardowy ekstraktor danych\nna pojedynczym, ręcznie wybranym pliku.\nSprawdź, czy pobiera oczekiwane dane\ni czy nie ma nieoczekiwanych efektów ubocznych."},
        'TEST_TOOLTIP':{
                "en":"Select a file and test your Custom Data Extractor.\n\n",
                "pl":"Wybierz plik i przetestuj swój niestandardowy ekstraktor danych.\n\n"},
        'Select Prev':{
                "pl":'Wybierz poprzedni'},
        'Select Next':{
                "pl":'Wybierz następny'},
        'Case Sensitive':{
                "pl":'Uwzględnij wiellkość znaków'},
        'index of the selected search result / search results total':{
                "pl":'indeks wybranego wyniku wyszukiwania / całkowita liczba wyników wyszukiwania '},
        'Abort searching.':{
                "pl":'Przerwij szukanie.'},
        'Rename / Repack record':{
                "pl":'Zmień nazwę / Przepakuj'},
        'Record Label':{
                "pl":'Identyfikator Rekordu'},
        'Data options':{
                "pl":'Opcje danych'},
        "Keep 'Custom Data'":{
                "pl":"Zachowaj 'Dane Użytkownika'"},
        'Compression (0-22)':{
                "pl":'Kompresja (0-22)'},
        'Proceed':{
                "pl":'Kontynuuj'},
        'Close':{
                "pl":'Zamknij'},
        'Where Is It ? Import Records':{
                "pl":'Where Is It ? importuj recordy'},
        'Options':{
                "pl":'Opcje'},
        ' Separate record per each disk (not recommended)':{
                "pl":' Oddzielny rekord dla każdego dysku (nie rekomendowane)'},
        'Common record label:':{
                "pl":'Wspólny identyfikator rekordu'},
        'Settings':{
                "pl":'Ustawienia'},
        'Show tooltips':{
                "pl":'Pokaż dymki z podpowiedziami'},
        'Record Info':{
                "pl":'Informacje o rekordzie'},
        'Choose record files to import':{
                "pl":'Wybierz pliki rekordów do zaimportowania'},
        'to group:':{
                "pl":'do grupy:'},
        'Import failed':{
                "pl":'Import nie powiódł się'},
        'Export':{
                "pl":'Eksport'},
        'Export failed':{
                "pl":'Eksport nie powiódł się'},
        'Where Is It? Import failed':{
                "pl":'Import z Where Is It? Nie powiódł się'},
        "No files / No folders":{
                "pl":'Brak plików / Brak folderów'},
        'Completed successfully.':{
                "pl":'Zakńczony pomyślnie.'},
        'Import completed successfully.':{
                "pl":'Import zakńczony pomyślnie.'},
        'Groups collapsed at startup':{
                "pl":'Zwiń grupy na starcie'},
        'Search records':{
                "pl":'Przeszukaj rekordy'},
        'Search range':{
                "pl":'Zakres Przeszukiwania'},
        ' Search:':{
                "pl":' Szukaj:'},
        'Selected record / group':{
                "pl":'Wybrany rekord / grupa'},
        'Case sensitive':{
                "pl":'Uwzględnij wielkość znaków'},
        'Threshold:':{
                "pl":'Próg:'},
        "Regular expression":{
                "pl":'Wyrażenie regularne'},
        'Custom Data':{
                "pl":'Dane użytkownika'},
        "No Custom Data":{
                "pl":'Brak danych użytkownika'},
        'Files without Custom Data':{
                "pl":'Pliki bez danych użytkownika'},
        "Any correct Custom Data":{
                "pl":'Jakiekolwiek poprawne dane użytkownika'},
        'Files with any correct Custom Data':{
                "pl":'Pliki z jakimikolwiek poprawnymi Danymi Użytkownika'},
        "Error on CD extraction":{
                "pl":'Błąd na ekstrakcji Danych Użytkownika'},
        'Files with error on CD extraction':{
                "pl":'Pliki z błędem na ekstrakcji Danych Użytkownika'},
        "No CD extracted (empty value)":{
                "pl":'Puste Dane Użytkownika'},
        'Files with empty CD value':{
                "pl":'Pliki z pustymi Danymi Użytkownika'},
        "CD extraction aborted":{
                "pl":'Przerwana ekstrakcja Danych Użytkownika'},
        'Files with aborted CD extraction':{
                "pl":'Pliki z przerwaną ekstrakcją Danych Użytkownika'},
        "Don't use this criterion":{
                "pl":'Nie używaj tego kryterium'},
        'regular expression error':{
                "pl":'błąd wyrażenia regularnego'},
        'regular expression empty':{
                "pl":'wyrażenie regularne puste'},
        'glob expression empty':{
                "pl":'wyrażenie "glob" puste'},
        'Search aborted.':{
                "pl":'Wyszukiwanie przerwane.'},
        'Delete selected group ?':{
                "pl":'Usuń wybraną grupę'},
        '(for Custom Data)':{
                "pl":'(Dla Danych Użytkownika)'},
        'No records.':{
                "pl":'Brak rekordów'},
        'group: ':{
                "pl":'grupa: '},
        '(Records assigned to group will remain untouched)':{
                "pl":'(Rekordy z grupy pozostanę nienaruszone)'},
        'Assign to group':{
                "pl":'Przypisz do grupy'},
        'Assign record to group:':{
                "pl":'Przypisz rekord do grupy'},
        'No paths to scan.':{
                "pl":'Brak ścieżek do skanowania'},
        'Add paths to scan.':{
                "pl":'Dodaj ścieżki do skanowania'},
        'Wrong mask expression':{
                "pl":'Błędne wyrażenie maski'},
        'Empty mask nr':{
                "pl":'Pusta ścieżka nr'},
        'Wrong executable':{
                "pl":'Błędny plik wykonywalny'},
        'Empty executable nr':{
                "pl":'Pusty plik wykonywalny nr'},
        'CDE Timeout not set':{
                "pl":'Nie ustawiony timeout CDE'},
        'Continue without Custom Data Extractor timeout ?':{
                "pl":'Kontynuować bez ustawionego timeoutu CDE ?'},
        'If you abort at this stage,\nData record will not be created.':{
                "pl":'Jeżeli przerwiesz na tym etapie,\nRekord danych nie zostanie utworzony.'},
        'CDE Total space:':{
                "pl":'Ilość danych CDE'},
        'CDE Files number:':{
                "pl":'Liczba plików CDE'},
        'Creating new data record (scanning)':{
                "pl":'Tworzenie nowego rekordu danych (skanowanie)'},
        'Creating new data record (Custom Data Extraction)':{
                "pl":'Tworzenie nowego rekordu danych (Ekstrakcja Danych Użytkownika)'},
        'Abort single file':{
                "pl":'Przerwij pojedynczy plik'},
        'If you abort at this stage,\nCustom Data will be incomplete.':{
                "pl":'Jeżeli przerwiesz na tym etapie,\nDane Użytkownika nie będą kompletne.'},
        'ABORT_PROGRESS_TOOLTIP':{
                "en":'Use if CDE has no timeout set and seems like stuck.\nCD of only single file will be incomplete.\nCDE will continue.\n\nAvailable only for single thread mode.',
                "pl":'Zastosuj jeżeli Eksttraktor CDE nie ma ustawionego timeoutu i utknął.\nCD pojedynczego pliku będzie niekompletny.\nEkstttrakcja będzie kontynuowana.\n\nDostępne tylko w trybie jednego wątku.'},
        'Extracted Custom Data: ':{
                "pl":'Wyekstraktowane Dane Użytkownika'},
        'Extraction Errors : ':{
                "pl":'Błędy Ekstrakcji : '},
        'Delete selected data record ?':{
                "pl":'Usunąć wybrany rekord danych ?'},
        'Create new data record in group:':{
                "pl":'Utwórz nowy rekord w grupie:'},
        'Create new data record':{
                "pl":'Utwórz nowy rekord'},
        "Opening dialog ...":{
                "pl":'Otwieranie dialogu ...'},
        'Select Directory':{
                "pl":'Wybierz katalog'},
        "Abort single pressed ...":{
                "pl":'Zastosowano przerwanie ...'},
        'Select File':{
                "pl":'Wybierz plik'},
        'All Files':{
                "pl":'Wszystkie pliki'},
        'Test Custom Data Extractor on selected file ?':{
                "pl":'Przetestować Ekstraktor Danych Użytkownika na wybranym pliku ?'},
        'Testing selected Custom Data Extractor':{
                "pl":'Testowanie Ekstraktora Danych Użytkownika'},
        'Full path copied to clipboard':{
                "pl":'Pełna ścieżka skopiowana do schowka'},
        'Copied to clipboard:':{
                "pl":'Skopiowana do schowka:'},
        'No':{
                "pl":'Nie'},
        'Yes':{
                "pl":'Tak'},
        'Information':{
                "pl":'Informacja'},
        'No Custom data.':{
                "pl":'Brak Danych Użytkownika'},
        'Language Changed':{
                "pl":'Język został zmieniony'},
        'Restart required.':{
                "pl":'Wymagany restart aplikacji.'},
        'Language:':{
                "pl":'Język:'},
        'Records':{
                "pl":'Rekordy'},
        'Include hidden files/folders in scan.':{
                "pl":'Uwzględniaj pliki/foldery ukryte.'},
    }

    def __init__(self):
        try:
            lang = getlocale()[0].split('_')[0]
            print(f'setting lang:{lang}')
        except:
            pass

    def set(self,lang_id):
        self.lang_id=lang_id

    def STR(self,str_par):
        try:
            return self.STR_DICT[str_par][self.lang_id]
        except:
            try:
                return self.STR_DICT[str_par]["en"]
            except:
                return str_par


