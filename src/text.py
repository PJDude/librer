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
    lang_dict={'Polski':'pl','English':'en','Español':'es','Русский':'ru','Deutsch':'de','Italiano':'it','Français':'fr'}

    STR_DICT={
        'Separate record per each disk (not recommended)': {
            'pl': 'Oddzielny rekord dla każdego dysku (nie rekomendowane)',
            'es': 'Registro separado por cada disco (no recomendado)',
            'ru': 'Отдельная запись для каждого диска (не рекомендуется)',
            'de': 'Getrennte Aufzeichnung für jede Festplatte (nicht empfohlen)',
            'it': 'Registrazione separata per ogni disco (non consigliato)',
            'fr': 'Enregistrement séparé pour chaque disque (non recommandé)'
        },
        '% File cryteria': {
            'pl': 'Kryteria plików %',
            'es': 'Criterios de archivos %',
            'ru': 'Критерии файла %',
            'de': 'Dateikriterien %',
            'it': 'Criteri del file %',
            'fr': 'Critères du fichier %'
        },
        '(Records assigned to group will remain untouched)': {
            'pl': '(Rekordy z grupy pozostaną nienaruszone)',
            'es': '(Los registros asignados al grupo permanecerán intactos)',
            'ru': '(Записи, назначенные группе, останутся нетронутыми)',
            'de': '(Auf Gruppen zugewiesene Datensätze bleiben unverändert)',
            'it': '(I record assegnati al gruppo rimarranno intatti)',
            'fr': '(Les enregistrements affectés au groupe resteront intacts)'
        },
        '(for Custom Data)': {
            'pl': '(Dla Danych Użytkownika)',
            'es': '(Para Datos del Usuario)',
            'ru': '(Для данных пользователя)',
            'de': '(Für Benutzerdaten)',
            'it': '(Per Dati dell\'Utente)',
            'fr': '(Pour les Données Utilisateur)'
        },
        'ABORT_PROGRESS_TOOLTIP': {
            'en': 'Use if CDE has no timeout set and seems like stuck.\nCD of only single file will be incomplete.\nCDE will continue.\n\nAvailable only for single thread mode.',
            'pl': 'Zastosuj jeżeli Eksttraktor CDE nie ma ustawionego timeoutu i utknął.\nCD pojedynczego pliku będzie niekompletny.\nEkstrakcja będzie kontynuowana.\n\nDostępne tylko w trybie jednego wątku.',
            'es': 'Úselo si CDE no tiene tiempo de espera configurado y parece estar atascado.\nEl CD de un solo archivo estará incompleto.\nCDE continuará.\n\nDisponible solo en modo de un solo hilo.',
            'ru': 'Используйте, если у CDE не установлен тайм-аут, и кажется, что программа зависла.\nCD только одного файла будет неполным.\nCDE продолжит.\n\nДоступно только в однопоточном режиме.',
            'de': 'Verwenden, wenn CDE keine Zeitüberschreitung eingestellt hat und festzustecken scheint.\nCD einer einzelnen Datei wird unvollständig sein.\nCDE wird fortgesetzt.\n\nNur im Einzelfadenmodus verfügbar.',
            'it': 'Usalo se CDE non ha un timeout impostato e sembra bloccato.\nIl CD di un singolo file sarà incompleto.\nCDE continuerà.\n\nDisponibile solo in modalità a singolo thread.',
            'fr': 'Utilisez si CDE n\'a pas de délai d\'attente défini et semble bloqué.\nLe CD d\'un seul fichier sera incomplet.\nCDE continuera.\n\nDisponible uniquement en mode mono-fil.'
        },
        'Abort': {
            'pl': 'Przerwij',
            'es': 'Abortar',
            'ru': 'Прервать',
            'de': 'Abbrechen',
            'it': 'Annulla',
            'fr': 'Annuler'
        },
        'Abort loading.': {
            'pl': 'Przerwij ładowanie',
            'es': 'Abortar carga.',
            'ru': 'Прервать загрузку.',
            'de': 'Laden abbrechen.',
            'it': 'Annulla il caricamento.',
            'fr': 'Annuler le chargement.'
        },
        'Abort pressed ...': {
            'pl': 'Użyto "Przerwij" ...',
            'es': 'Se presionó "Abortar"...',
            'ru': 'Нажата кнопка "Прервать"...',
            'de': '"Abbrechen" gedrückt...',
            'it': 'Premuto "Annulla"...',
            'fr': 'Bouton "Annuler" pressé...'
        },
        'Abort searching.': {
            'pl': 'Przerwij szukanie.',
            'es': 'Abortar búsqueda.',
            'ru': 'Прервать поиск.',
            'de': 'Suche abbrechen.',
            'it': 'Annulla la ricerca.',
            'fr': 'Annuler la recherche.'
        },
        'Abort single file': {
            'pl': 'Przerwij plik',
            'es': 'Abortar archivo único',
            'ru': 'Прервать одиночный файл',
            'de': 'Einzelne Datei abbrechen',
            'it': 'Annulla il singolo file',
            'fr': 'Annuler le fichier unique'
        },
        'Abort single pressed ...': {
            'pl': 'Zastosowano przerwanie ...',
            'es': 'Se presionó la interrupción ...',
            'ru': 'Применено прерывание ...',
            'de': 'Unterbrechung angewendet ...',
            'it': 'Interruzione applicata ...',
            'fr': 'Interruption appliquée ...'
        },
        'About': {
            'pl': 'O programie',
            'es': 'Acerca de',
            'ru': 'О программе',
            'de': 'Über',
            'it': 'Info',
            'fr': 'À propos'
        },
        'Add paths to scan.': {
            'pl': 'Dodaj ścieżki do skanowania',
            'es': 'Agregar rutas para escanear.',
            'ru': 'Добавить пути для сканирования.',
            'de': 'Pfad zum Scannen hinzufügen.',
            'it': 'Aggiungi percorsi da scansionare.',
            'fr': 'Ajouter des chemins à analyser.'
        },
        'Alias record name': {
            'pl': 'Alias nazwy rekordu',
            'es': 'Nombre alias del registro',
            'ru': 'Псевдоним имени записи',
            'de': 'Alias des Datensatznamens',
            'it': 'Nome alias del record',
            'fr': 'Nom alias de l\'enregistrement'
        },
        'All Files': {
            'pl': 'Wszystkie pliki',
            'es': 'Todos los archivos',
            'ru': 'Все файлы',
            'de': 'Alle Dateien',
            'it': 'Tutti i file',
            'fr': 'Tous les fichiers'
        },
        'All records': {
            'pl': 'Wszystkie rekordy',
            'es': 'Todos los registros',
            'ru': 'Все записи',
            'de': 'Alle Datensätze',
            'it': 'Tutti i record',
            'fr': 'Tous les enregistrements'
        },
        'All records in repository': {
            'pl': 'Wszystkie rekordy w repozytorium',
            'es': 'Todos los registros en el repositorio',
            'ru': 'Все записи в репозитории',
            'de': 'Alle Datensätze im Repository',
            'it': 'Tutti i record nel repository',
            'fr': 'Tous les enregistrements dans le référentiel'
        },
        'Any correct Custom Data': {
            'pl': 'Jakiekolwiek poprawne dane Użytkownika',
            'es': 'Cualquier dato de usuario correcto',
            'ru': 'Любые правильные данные пользователя',
            'de': 'Irgendeine korrekte Benutzerdaten',
            'it': 'Qualsiasi dato utente corretto',
            'fr': 'Données utilisateur correctes'
        },
        'Application restart required\nfor changes to take effect': {
            'pl': 'Aby zmiany zostały wprowadzone\nwymagane jest ponowne uruchomienie aplikacji.',
            'es': 'Se requiere reiniciar la aplicación\npara que los cambios surtan efecto.',
            'ru': 'Для применения изменений\nтребуется перезапуск приложения.',
            'de': 'Ein Neustart der Anwendung ist erforderlich,\num Änderungen wirksam zu machen.',
            'it': 'È necessario riavviare l\'applicazione\nper applicare le modifiche.',
            'fr': 'Le redémarrage de l\'application est requis\npour appliquer les modifications.'
        },
        'Assign record to group ...': {
            'pl': 'Przypisz rekord do grupy ...',
            'es': 'Asignar registro al grupo ...',
            'ru': 'Назначить запись в группу ...',
            'de': 'Datensatz der Gruppe zuweisen ...',
            'it': 'Assegna record al gruppo ...',
            'fr': 'Attribuer un enregistrement au groupe ...'
        },
        'Assign record to group:': {
            'pl': 'Przypisz rekord do grupy',
            'es': 'Asignar registro al grupo:',
            'ru': 'Назначить запись в группу:',
            'de': 'Datensatz der Gruppe zuweisen:',
            'it': 'Assegna record al gruppo:',
            'fr': 'Attribuer un enregistrement au groupe:'
        },
        'Assign to group': {
            'pl': 'Przypisz do grupy',
            'es': 'Asignar al grupo',
            'ru': 'Назначить в группу',
            'de': 'Gruppe zuweisen',
            'it': 'Assegna al gruppo',
            'fr': 'Attribuer au groupe'
        },
        'Bash Files':{
            'pl':'Pliki Bash',
            'es':'Archivos Bash',
            'ru':'Файлы Bash',
            'de':'Bash-Dateien',
            'it':'File Bash',
            'fr':'Fichiers Bash',
        },
        'Bat Files':{
            'pl':'Pliki bat',
            'es':'Archivos bat',
            'ru':'Bat-файлы',
            'de':'Bat-Dateien',
            'it':'File bat',
            'fr':'Fichiers bat',
        },
        'Binding (another device)':{
            'pl':'Dowiązanie (inne urządzenie)',
            'es':'Vinculación (otro dispositivo)',
            'ru':'Привязка (другие устройства)',
            'de':'Bindung (anderes Gerät)',
            'it':'Binding (altro dispositivo)',
            'fr':'Liaison (autre appareil)',
        },
        'By fuzzy match':{
            'pl':'Poprzez dopasowanie rozmyte',
            'es':'Por coincidencia difusa',
            'ru':'По нечеткому совпадению',
            'de':'Durch unscharfe Übereinstimmung',
            'it':'Per corrispondenza imprecisa',
            'fr':'Par correspondance floue',
        },
        'By glob pattern':{
            'pl':'Poprzez wyrażenie "glob"',
            'es':'Por patrón glob',
            'ru':'По шаблону glob',
            'de':'Durch Glob-Muster',
            'it':'Per modello glob',
            'fr':'Par motif glob',
        },
        'By regular expression':{
            'pl':'Poprzez wyrażenie regularne',
            'es':'Por expresión regular',
            'ru':'По регулярному выражению',
            'de':'Durch regulären Ausdruck',
            'it':'Per espressione regolare',
            'fr':'Par expression régulière',
        },
        'CD extraction aborted':{
            'pl':'Przerwana ekstrakcja Danych Użytkownika',
            'es':'Extracción de Datos del Usuario abortada',
            'ru':'Извлечение пользовательских данных прервано',
            'de':'Extraktion von Benutzerdaten abgebrochen',
            'it':'Estrazione dei Dati Utente interrotta',
            'fr':'Extraction des Données Utilisateur interrompue',
        },
        'CDE Files number:':{
            'pl':'Liczba plików CDE',
            'es':'Número de archivos CDE',
            'ru':'Количество файлов CDE',
            'de':'Anzahl der CDE-Dateien',
            'it':'Numero di file CDE',
            'fr':'Nombre de fichiers CDE',
        },
        'CDE Test finished':{
            'pl':'EDU Test zakończony',
            'es':'Prueba CDE terminada',
            'ru':'Тест CDE завершен',
            'de':'CDE-Test abgeschlossen',
            'it':'Test CDE terminato',
            'fr':'Test CDE terminé',
        },
        'CDE Threads:':{
            'pl':'Wątki CDE:',
            'es':'Hilos CDE:',
            'ru':'Потоки CDE:',
            'de':'CDE-Threads:',
            'it':'Thread CDE:',
            'fr':'Fils CDE :',
        },
        'CDE Timeout not set':{
            'pl':'Nie ustawiony timeout CDE',
            'es':'Timeout CDE no configurado',
            'ru':'Тайм-аут CDE не установлен',
            'de':'CDE-Timeout nicht gesetzt',
            'it':'Timeout CDE non impostato',
            'fr':'Timeout CDE non défini',
        },
        'CDE Total space:':{
            'pl':'Ilość danych CDE',
            'es':'Espacio total CDE',
            'ru':'Общий объём данных CDE',
            'de':'Gesamtgröße der CDE-Daten:',
            'it':'Spazio totale CDE',
            'fr':'Espace total CDE',
        },
        'Cancel':{
            'pl':'Anuluj',
            'es':'Cancelar',
            'ru':'Отменить',
            'de':'Abbrechen',
            'it':'Annulla',
            'fr':'Annuler',
        },
        'Case Sensitive':{
            'pl':'Uwzględnij wiellkość znaków',
            'es':'Sensible a mayúsculas/minúsculas',
            'ru':'Чувствительность к регистру',
            'de':'Groß-/Kleinschreibung beachten',
            'it':'Sensibile al maiuscolo/minuscolo',
            'fr':'Sensible à la casse',
        },
        'Check repacked record\nDelete original record manually if you want.':{
            'pl':'Sprawdź ponownie spakowany rekord\nJeśli chcesz, usuń ręcznie oryginalny rekord.',
            'es':'Verifica el registro reempaquetado\nElimina el registro original manualmente si lo deseas.',
            'ru':'Проверьте повторно упакованный запись\nУдалите оригинальную запись вручную, если хотите.',
            'de':'Überprüfen Sie das erneut verpackte Protokoll\nLöschen Sie das Originalprotokoll manuell, wenn Sie möchten.',
            'it':'Controlla il record ripacchettato\nElimina manualmente il record originale se lo desideri.',
            'fr':'Vérifiez l’enregistrement reconditionné\nSupprimez l’enregistrement original manuellement si vous le souhaitez.',
        },
        'Checked on the entire\nCustom Data of a file.':{
            'pl':'Sprawdzono na wszystkich\nDanych niestandardowych pliku.',
            'es':'Verificado en todos los\nDatos personalizados del archivo.',
            'ru':'Проверено на всех\nПользовательских данных файла.',
            'de':'Überprüft auf allen\nBenutzerdaten einer Datei.',
            'it':'Verificato su tutti i\nDati utente del file.',
            'fr':'Vérifié sur toutes les\nDonnées utilisateur du fichier.',
        },
        'Checked on the file or folder name.':{
            'pl':'Sprawdzane na nazwie pliku lub folderu.',
            'es':'Verificado en el nombre del archivo o carpeta.',
            'ru':'Проверено по имени файла или папки.',
            'de':'Überprüft anhand des Dateinamens oder Ordners.',
            'it':'Verificato sul nome del file o della cartella.',
            'fr':'Vérifié sur le nom du fichier ou du dossier.',
        },
        'Checking records to load ...':{
            'pl':'Sprawdzanie rekordu do załadowania ...',
            'es':'Comprobando registros para cargar...',
            'ru':'Проверка записей для загрузки...',
            'de':'Prüfe Datensätze zum Laden...',
            'it':'Controllo dei record da caricare...',
            'fr':'Vérification des enregistrements à charger...',
        },
        'Choose "Where Is It?" Report xml files to import':{
            'pl':'Wybierz raport z "Where Is It?" do importowania',
            'es':'Elija los archivos XML del informe "Where Is It?" para importar',
            'ru':'Выберите XML-файлы отчета "Where Is It?" для импорта',
            'de':'Wählen Sie "Where Is It?"-Bericht XML-Dateien zum Importieren',
            'it':'Scegli i file XML del rapporto "Where Is It?" da importare',
            'fr':'Choisissez les fichiers XML du rapport "Where Is It ?" à importer',
        },
        'Choose record files to import':{
            'pl':'Wybierz pliki rekordów do zaimportowania',
            'es':'Elija los archivos de registro para importar',
            'ru':'Выберите файлы записей для импорта',
            'de':'Wählen Sie Aufzeichnungsdateien zum Importieren',
            'it':'Scegli i file di registro da importare',
            'fr':'Choisissez les fichiers de registre à importer',
        },
        'Clear Search Results':{
            'pl':'Wyczyść wyniki wyszukiwania',
            'es':'Borrar resultados de búsqueda',
            'ru':'Очистить результаты поиска',
            'de':'Suchergebnisse löschen',
            'it':'Cancella risultati di ricerca',
            'fr':'Effacer les résultats de recherche',
        },
        'Click to show full record info':{
            'pl':'Kliknij by pokazać informacje o rekordzie',
            'es':'Haz clic para mostrar la información completa del registro',
            'ru':'Щелкните, чтобы показать полную информацию о записи',
            'de':'Klicken Sie, um die vollständigen Aufzeichnungsinformationen anzuzeigen',
            'it':'Clicca per mostrare le informazioni complete del record',
            'fr':'Cliquez pour afficher les informations complètes du registre',
        },
        'Click to unload (free memory) data of selected record\nDouble click to unload data of all records.':{
            'pl':'Kliknij, aby odładować (zwolnić pamięć) dane wybranego rekordu\nKliknij dwukrotnie, aby odładować dane wszystkich rekordów.',
            'es':'Haz clic para descargar (liberar memoria) los datos del registro seleccionado\nHaz doble clic para descargar los datos de todos los registros.',
            'ru':'Щелкните, чтобы выгрузить (освободить память) данные выбранной записи\nДважды щелкните, чтобы выгрузить данные всех записей.',
            'de':'Klicken Sie, um die Daten des ausgewählten Datensatzes zu entladen (Speicher freigeben)\nDoppelklicken Sie, um die Daten aller Datensätze zu entladen.',
            'it':'Fai clic per scaricare (liberare memoria) i dati del record selezionato\nFai doppio clic per scaricare i dati di tutti i record.',
            'fr':'Cliquez pour décharger (libérer de la mémoire) les données de l’enregistrement sélectionné\nDouble-cliquez pour décharger les données de tous les enregistrements.',
        },
        'Close':{
            'pl':'Zamknij',
            'es':'Cerrar',
            'ru':'Закрыть',
            'de':'Schließen',
            'it':'Chiudi',
            'fr':'Fermer',
        },
        'Common record label:':{
            'pl':'Wspólny identyfikator rekordu',
            'es':'Etiqueta de registro común',
            'ru':'Общий ярлык записи',
            'de':'Gemeinsames Datensatzetikett',
            'it':'Etichetta del record comune',
            'fr':'Étiquette d’enregistrement commune',
        },
        'Completed successfully.':{
            'pl':'Zakończony pomyślnie.',
            'es':'Completado con éxito.',
            'ru':'Завершено успешно.',
            'de':'Erfolgreich abgeschlossen.',
            'it':'Completato con successo.',
            'fr':'Terminé avec succès.',
        },
        'Compression (0-22)':{
            'pl':'Kompresja (0-22)',
            'es':'Compresión (0-22)',
            'ru':'Сжатие (0-22)',
            'de':'Kompression (0-22)',
            'it':'Compressione (0-22)',
            'fr':'Compression (0-22)',
        },
        'Compression:':{
            'pl':'Kompresja:',
            'es':'Compresión:',
            'ru':'Сжатие:',
            'de':'Kompression:',
            'it':'Compressione:',
            'fr':'Compression :',
        },
        'Continue search':{
            'pl':'Szukaj dalej',
            'es':'Continuar búsqueda',
            'ru':'Продолжить поиск',
            'de':'Suche fortsetzen',
            'it':'Continua ricerca',
            'fr':'Continuer la recherche',
        },
        'Continue without Custom Data Extractor timeout ?':{
            'pl':'Kontynuować bez ustawionego timeoutu CDE ?',
            'es':'¿Continuar sin configurar el tiempo de espera del Extractor de Datos del Usuario?',
            'ru':'Продолжить без установленного тайм-аута CDE?',
            'de':'Ohne CDE-Timeout fortfahren?',
            'it':'Continuare senza impostare il timeout dell\'Estrattore di Dati Utente?',
            'fr':'Continuer sans définir le délai d\'attente de l\'extracteur de données utilisateur?',
        },
        'Copied to clipboard:':{
            'pl':'Skopiowana do schowka:',
            'es':'Copiado al portapapeles:',
            'ru':'Скопировано в буфер обмена:',
            'de':'In Zwischenablage kopiert:',
            'it':'Copiato negli appunti:',
            'fr':'Copié dans le presse-papiers:',
        },
        'Copy':{
            'pl':'Kopiuj',
            'es':'Copiar',
            'ru':'Копировать',
            'de':'Kopieren',
            'it':'Copia',
            'fr':'Copier',
        },
        'Copy full path':{
            'pl':'Kopiuj pełną ścieżkę',
            'es':'Copiar ruta completa',
            'ru':'Копировать полный путь',
            'de':'Vollständigen Pfad kopieren',
            'it':'Copia il percorso completo',
            'fr':'Copier le chemin complet',
        },
        'Create new data record':{
            'pl':'Utwórz nowy rekord',
            'es':'Crear nuevo registro de datos',
            'ru':'Создать новую запись данных',
            'de':'Neuen Datensatz erstellen',
            'it':'Crea nuovo record di dati',
            'fr':'Créer un nouvel enregistrement de données',
        },
        'Create new data record in group:':{
            'pl':'Utwórz nowy rekord w grupie:',
            'es':'Crear nuevo registro de datos en grupo:',
            'ru':'Создать новую запись данных в группе:',
            'de':'Neuen Datensatz in der Gruppe erstellen:',
            'it':'Crea un nuovo record di dati nel gruppo:',
            'fr':'Créer un nouvel enregistrement de données dans le groupe :',
        },
        'Creating dialog ...':{
            'pl':'Tworzenie dialogu" ... ',
            'es':'Creando el diálogo ...',
            'ru':'Создание диалога ...',
            'de':'Dialog erstellen ...',
            'it':'Creando il dialogo ...',
            'fr':'Création du dialogue ...',
        },
        'Creating new data record (Custom Data Extraction)':{
            'pl':'Tworzenie nowego rekordu danych (Ekstrakcja Danych Użytkownika)',
            'es':'Creando nuevo registro de datos (Extracción de Datos del Usuario)',
            'ru':'Создание новой записи данных (Извлечение пользовательских данных)',
            'de':'Erstellen eines neuen Datensatzes (Benutzerdatenextraktion)',
            'it':'Creazione di un nuovo record di dati (Estrazione dei Dati Utente)',
            'fr':'Création d’un nouvel enregistrement de données (Extraction des Données Utilisateur)',
        },
        'Creating new data record (scanning)':{
            'pl':'Tworzenie nowego rekordu danych (skanowanie)',
            'es':'Creando nuevo registro de datos (escaneo)',
            'ru':'Создание новой записи данных (сканирование)',
            'de':'Erstellen eines neuen Datensatzes (Scannen)',
            'it':'Creazione di un nuovo record di dati (scansione)',
            'fr':'Création d’un nouvel enregistrement de données (scannage)',
        },
        'Custom Data':{
            'pl':'Dane Użytkownika',
            'es':'Datos del Usuario',
            'ru':'Пользовательские данные',
            'de':'Benutzerdaten',
            'it':'Dati Utente',
            'fr':'Données utilisateur',
        },
        'Custom Data Extraction ended with error':{
            'pl':'Ekstrakcja Danych Użytkownika zakończona błędem',
            'es':'Extracción de Datos del Usuario finalizada con error',
            'ru':'Извлечение пользовательских данных завершено с ошибкой',
            'de':'Benutzerdatenextraktion mit Fehler beendet',
            'it':'Estrazione dei Dati Utente terminata con errore',
            'fr':'L\'extraction des Données Utilisateur s\'est terminée avec une erreur',
        },
        'Custom Data Extraction was aborted':{
            'pl':'Ekstrakcja Danych Użytkownika została przerwana',
            'es':'Extracción de Datos del Usuario fue abortada',
            'ru':'Извлечение пользовательских данных было прервано',
            'de':'Benutzerdatenextraktion wurde abgebrochen',
            'it':'Estrazione dei Dati Utente interrotta',
            'fr':'L\'extraction des Données Utilisateur a été interrompue',
        },
        'Custom Data Extractors:':{
            'pl':'Ekstraktory Danych Użytkownika:',
            'es':'Extractores de Datos del Usuario:',
            'ru':'Экстракторы пользовательских данных:',
            'de':'Benutzerdatenextraktoren:',
            'it':'Estraitori di Dati Utente:',
            'fr':'Extracteurs de Données Utilisateur :',
        },
        'Custom Data extractor command':{
            'pl':'Kryteria plików %',
            'es':'Comando del extractor de Datos del Usuario',
            'ru':'Команда экстрактора пользовательских данных',
            'de':'Benutzerdatenextraktor-Befehl',
            'it':'Comando estrattore di Dati Utente',
            'fr':'Commande de l\'extracteur de Données Utilisateur',
        },
        'Custom Data is empty':{
            'pl':'Dane Użytkownika są puste',
            'es':'Los Datos del Usuario están vacíos',
            'ru':'Пользовательские данные пусты',
            'de':'Benutzerdaten sind leer',
            'it':'I Dati Utente sono vuoti',
            'fr':'Les Données Utilisateur sont vides',
        },
        'Custom Data of':{
            'pl':'Dane Użytkownika pliku',
            'es':'Datos del Usuario del archivo',
            'ru':'Пользовательские данные файла',
            'de':'Benutzerdaten der Datei',
            'it':'Dati Utente del file',
            'fr':'Données Utilisateur du fichier',
        },
        'Dat Files': {
            'pl': 'Pliki Dat',
            'es': 'Archivos Dat',
            'ru': 'Файлы Dat',
            'de': 'Dat-Dateien',
            'it': 'File Dat',
            'fr': 'Fichiers Dat'
        },
        'Data options': {
            'pl': 'Opcje danych',
            'es': 'Opciones de datos',
            'ru': 'Параметры данных',
            'de': 'Datenoptionen',
            'it': 'Opzioni dei dati',
            'fr': 'Options de données'
        },
        'Data record internal compression. A higher value\nmeans a smaller file and longer compression time.\nvalues above 20 may result in extremely long compression\nand memory consumption. The default value is 9.': {
            'pl': 'Kompresja wewnętrzna rekordu danych. Wyższa wartość\noznacza mniejszy plik i dłuższy czas kompresji.\nWartości powyżej 20 mogą skutkować ekstremalnie długą\nkompresją i zużyciem pamięci. Wartość domyślna to 9.',
            'es': 'Compresión interna del registro de datos. Un valor más alto\nsignifica un archivo más pequeño y un tiempo de compresión más largo.\nValores superiores a 20 pueden resultar en compresión extremadamente larga\ny un consumo de memoria elevado. El valor predeterminado es 9.',
            'ru': 'Внутренняя сжатие записи данных. Более высокое значение\nозначает меньший файл и более долгое время сжатия.\nЗначения выше 20 могут привести к чрезвычайно долгому сжатию\nи большому потреблению памяти. Значение по умолчанию - 9.',
            'de': 'Interne Kompression des Datenobjekts. Ein höherer Wert\nbedeutet eine kleinere Datei und eine längere Kompressionszeit.\nWerte über 20 können zu extrem langen Kompressionszeiten\nund Speicherverbrauch führen. Der Standardwert ist 9.',
            'it': 'Compressione interna del record dei dati. Un valore più alto\nsignifica un file più piccolo e un tempo di compressione più lungo.\nI valori superiori a 20 possono causare una compressione estremamente lunga\ne un elevato consumo di memoria. Il valore predefinito è 9.',
            'fr': 'Compression interne du fichier de données. Une valeur plus élevée\nsignifie un fichier plus petit et un temps de compression plus long.\nDes valeurs supérieures à 20 peuvent entraîner une compression extrêmement longue\net une consommation de mémoire. La valeur par défaut est 9.'
        },
        'Delete record ...': {
            'pl': 'Skasuj rekord ...',
            'es': 'Eliminar registro ...',
            'ru': 'Удалить запись ...',
            'de': 'Datensatz löschen ...',
            'it': 'Elimina record ...',
            'fr': 'Supprimer l\'enregistrement ...'
        },
        'Delete selected data record ?': {
            'pl': 'Usunąć wybrany rekord danych ?',
            'es': '¿Eliminar el registro de datos seleccionado?',
            'ru': 'Удалить выбранную запись данных ?',
            'de': 'Ausgewählten Datensatz löschen ?',
            'it': 'Eliminare il record dei dati selezionato?',
            'fr': 'Supprimer le registre de données sélectionné ?'
        },
        'Delete selected group ?': {
            'pl': 'Usuń wybraną grupę',
            'es': '¿Eliminar el grupo seleccionado?',
            'ru': 'Удалить выбранную группу ?',
            'de': 'Ausgewählte Gruppe löschen ?',
            'it': 'Eliminare il gruppo selezionato ?',
            'fr': 'Supprimer le groupe sélectionné ?'
        },
        "Don't cross device boundaries (mount points, bindings etc.) - recommended": {
            'pl': 'Nie przekraczaj granic urządzeń (punktów montowania, powiązań itp.) - zalecane',
            'es': 'No cruces los límites de dispositivo (puntos de montaje, enlaces, etc.) - recomendado',
            'ru': 'Не пересекайте границы устройств (точки монтирования, привязки и т.д.) - рекомендуется',
            'de': 'Überschreiten Sie keine Gerätegrenzen (Mount-Punkte, Bindungen usw.) - empfohlen',
            'it': 'Non attraversare i confini dei dispositivi (punti di montaggio, collegamenti, ecc.) - consigliato',
            'fr': 'Ne franchissez pas les limites des périphériques (points de montage, liaisons, etc.) - recommandé'
        },
        "Don't use this criterion": {
            'pl': 'Nie używaj tego kryterium',
            'es': 'No uses este criterio',
            'ru': 'Не используйте этот критерий',
            'de': 'Verwenden Sie dieses Kriterium nicht',
            'it': 'Non utilizzare questo criterio',
            'fr': 'Ne pas utiliser ce critère'
        },
        'Double click to show Custom Data': {
            'pl': 'Kliknij dwukrotnie, aby wyświetlić Dane Użytkownika',
            'es': 'Haz doble clic para mostrar los Datos del Usuario',
            'ru': 'Дважды щелкните, чтобы показать данные пользователя',
            'de': 'Doppelklicken Sie, um Benutzerdaten anzuzeigen',
            'it': 'Fai doppio clic per mostrare i Dati dell\'utente',
            'fr': 'Double-cliquez pour afficher les Données utilisateur'
        },
        'Double click to show full record info': {
            'pl': 'Kliknij dwukrotnie, aby wyświetlić pełne informacje o rekordzie',
            'es': 'Haz doble clic para mostrar la información completa del registro',
            'ru': 'Дважды щелкните, чтобы показать полную информацию о записи',
            'de': 'Doppelklicken Sie, um vollständige Informationen zum Datensatz anzuzeigen',
            'it': 'Fai doppio clic per visualizzare tutte le informazioni sul record',
            'fr': 'Double-cliquez pour afficher les informations complètes sur l\'enregistrement'
        },
        'EXEC_TOOLTIP': {
            'en': "Binary executable, batch script, or entire command\n(depending on the 'shell' option setting)\nthat will run with the full path to the scanned file.\nThe executable may have a full path, be located in a PATH\nenvironment variable, or be interpreted by the system shell\n\ncheck 'shell' option tooltip.",
            'pl': 'Plik wykonywalny binarny, skrypt wsadowy lub całe polecenie\n(w zależności od ustawienia opcji "shell")\nktóre zostanie uruchomione z pełną ścieżką do skanowanego pliku.\nPlik wykonywalny może mieć pełną ścieżkę, znajdować się w zmiennej\nśrodowiskowej PATH lub być interpretowany przez powłokę systemową\n\nSprawdź podpowiedź opcji "shell".',
            'es': 'Archivo ejecutable binario, script por lotes o comando completo\n(depende de la configuración de la opción "shell")\nque se ejecutará con la ruta completa al archivo escaneado.\nEl ejecutable puede tener una ruta completa, estar ubicado en una variable de entorno PATH\no ser interpretado por el shell del sistema\n\nVerifique la descripción de la opción "shell".',
            'ru': 'Двоичный исполнимый файл, пакетный скрипт или команда\n(в зависимости от настройки опции "shell")\nкоторая будет выполняться с полным путем к сканируемому файлу.\nИсполнимый файл может иметь полный путь, находиться в переменной окружения PATH\nили быть интерпретирован системой оболочки\n\nпроверьте подсказку для опции "shell".',
            'de': 'Binäre ausführbare Datei, Batch-Skript oder gesamtes Kommando\n(je nach Einstellung der "shell"-Option)\ndas mit dem vollständigen Pfad zur gescannten Datei ausgeführt wird.\nDie ausführbare Datei kann einen vollständigen Pfad haben, sich in einer PATH-Umgebungsvariable befinden\noder vom System-Shell interpretiert werden\n\nÜberprüfen Sie die Tooltipp-Option "shell".',
            'it': 'File eseguibile binario, script batch o comando completo\n(a seconda delle impostazioni dell\'opzione "shell")\nche verrà eseguito con il percorso completo del file scansionato.\nL\'eseguibile può avere un percorso completo, trovarsi in una variabile di ambiente PATH\noppure essere interpretato dalla shell del sistema\n\nverifica il suggerimento dell\'opzione "shell".',
            'fr': 'Exécutable binaire, script par lot ou commande complète\n(en fonction de la configuration de l\'option "shell")\nqui sera exécuté avec le chemin complet vers le fichier scanné.\nL\'exécutable peut avoir un chemin complet, être situé dans une variable d\'environnement PATH\nou être interprété par le shell du système\n\nvérifiez l\'astuce de l\'option "shell".'
        },
        'GLOB_TOOLTIP': {
            'en': "An expression containing wildcard characters\nsuch as '*','?' or character range '[a-c]'.\n\nPlace '*' at the beginning and end of an expression\nunless you want the expression to be found exactly\nat the beginning or end of a path element\n\n",
            'pl': "Wyrażenie zawierające znaki wieloznaczne\nnp. '*', '?' lub zakres znaków '[a-c]'.\n\nUmieść '*' na początku i na końcu wyrażenia\nchyba że chcesz, aby wyrażenie zostało znalezione dokładnie\nna początku lub na końcu elementu ścieżki\n\n",
            'es': "Una expresión que contiene caracteres comodín\ncomo '*', '?' o un rango de caracteres '[a-c]'.\n\nColoque '*' al principio y al final de una expresión\na menos que desee que la expresión se encuentre exactamente\nal principio o al final de un elemento de la ruta\n\n",
            'ru': "Выражение, содержащее подстановочные символы\nтакие как '*', '?' или диапазон символов '[a-c]'.\n\nПоместите '*' в начало и конец выражения,\nесли вы не хотите, чтобы выражение находилось\nточно в начале или конце элемента пути\n\n",
            'de': "Ein Ausdruck mit Platzhaltern\nwie '*', '?' oder einem Zeichenbereich '[a-c]'.\n\nSetzen Sie '*' an den Anfang und das Ende eines Ausdrucks,\nsofern Sie nicht möchten, dass der Ausdruck\nexakt am Anfang oder Ende eines Pfadelements gefunden wird\n\n",
            'it': "Un'espressione contenente caratteri jolly\ncome '*', '?' o un intervallo di caratteri '[a-c]'.\n\nMetti '*' all'inizio e alla fine di un'espressione\na meno che tu non voglia che l'espressione venga trovata\nesattamente all'inizio o alla fine di un elemento del percorso\n\n",
            'fr': "Une expression contenant des caractères génériques\ncomme '*', '?' ou une plage de caractères '[a-c]'.\n\nPlacez '*' au début et à la fin d'une expression\nà moins que vous ne souhaitiez que l'expression soit trouvée\nexactement au début ou à la fin d'un élément de chemin\n\n",
        },
        'Glob expression on Custom Data': {
            'pl': "Wyrażenie 'glob' na Danych Użytkownika",
            'es': "Expresión 'glob' en Datos de Usuario",
            'ru': "Выражение 'glob' для пользовательских данных",
            'de': "'Glob'-Ausdruck für Benutzerdaten",
            'it': "Espressione 'glob' sui Dati Utente",
            'fr': "Expression 'glob' sur les Données Utilisateur",
        },
        'Glob expression on path element': {
            'pl': "Wyrażenie glob na elementach ścieżki",
            'es': "Expresión glob en elementos de ruta",
            'ru': "Выражение glob для элемента пути",
            'de': "Glob-Ausdruck für Pfadelemente",
            'it': "Espressione glob sugli elementi del percorso",
            'fr': "Expression glob sur les éléments de chemin",
        },
        'Go to first record': {
            'pl': "Idź do pierwszego rekordu",
            'es': "Ir al primer registro",
            'ru': "Перейти к первой записи",
            'de': "Zum ersten Datensatz gehen",
            'it': "Vai al primo record",
            'fr': "Aller au premier enregistrement",
        },
        'Go to last record': {
            'pl': "Idź do ostatniego rekordu",
            'es': "Ir al último registro",
            'ru': "Перейти к последней записи",
            'de': "Zum letzten Datensatz gehen",
            'it': "Vai all'ultimo record",
            'fr': "Aller au dernier enregistrement",
        },
        'Go to next record': {
            'pl': "Idź do następnego rekordu",
            'es': "Ir al siguiente registro",
            'ru': "Перейти к следующей записи",
            'de': "Zum nächsten Datensatz gehen",
            'it': "Vai al record successivo",
            'fr': "Aller à l'enregistrement suivant",
        },
        'Go to previous record': {
            'pl': "Idź do poprzedniego rekordu",
            'es': "Ir al registro anterior",
            'ru': "Перейти к предыдущей записи",
            'de': "Zum vorherigen Datensatz gehen",
            'it': "Vai al record precedente",
            'fr': "Aller à l'enregistrement précédent",
        },
        'Group': {
            'pl': "Grupa",
            'es': "Grupo",
            'ru': "Группа",
            'de': "Gruppe",
            'it': "Gruppo",
            'fr': "Groupe",
        },
        'Groups collapsed at startup': {
            'pl': "Zwiń grupy na starcie",
            'es': "Grupos colapsados al inicio",
            'ru': "Группы свёрнуты при запуске",
            'de': "Gruppen beim Start eingeklappt",
            'it': "Gruppi compressi all'avvio",
            'fr': "Groupes réduits au démarrage",
        },
        'Help': {
            'pl': "Pomoc",
            'es': "Ayuda",
            'ru': "Помощь",
            'de': "Hilfe",
            'it': "Aiuto",
            'fr': "Aide",
        },
        'If you abort at this stage,\nCustom Data will be incomplete.': {
            'pl': "Jeżeli przerwiesz na tym etapie,\nDane Użytkownika nie będą kompletne.",
            'es': "Si cancelas en esta etapa,\nlos Datos de Usuario estarán incompletos.",
            'ru': "Если вы прервёте на этом этапе,\nданные пользователя будут неполными.",
            'de': "Wenn Sie an dieser Stelle abbrechen,\nsind die Benutzerdaten unvollständig.",
            'it': "Se annulli in questa fase,\ni Dati Utente saranno incompleti.",
            'fr': "Si vous annulez à ce stade,\nles Données Utilisateur seront incomplètes.",
        },
        'If you abort at this stage,\nData record will not be created.': {
            'pl': "Jeżeli przerwiesz na tym etapie,\nRekord danych nie zostanie utworzony.",
            'es': "Si cancelas en esta etapa,\nel registro de datos no se creará.",
            'ru': "Если вы прервёте на этом этапе,\nзапись данных не будет создана.",
            'de': "Wenn Sie an dieser Stelle abbrechen,\nwird der Datensatz nicht erstellt.",
            'it': "Se annulli in questa fase,\nil record di dati non sarà creato.",
            'fr': "Si vous annulez à ce stade,\nl'enregistrement de données ne sera pas créé.",
        },
        'Import "Where Is It?" xml ...': {
            'pl': 'Importuj xml z "Where Is It?" ...',
            'es': 'Importar xml de "Where Is It?" ...',
            'ru': 'Импортировать xml из "Where Is It?" ...',
            'de': 'Importiere XML aus "Where Is It?" ...',
            'it': 'Importa xml da "Where Is It?" ...',
            'fr': 'Importer xml de "Where Is It?" ...',
        },
        'Import Record ...': {
            'pl': "Importuj rekord ...",
            'es': "Importar registro ...",
            'ru': "Импортировать запись ...",
            'de': "Datensatz importieren ...",
            'it': "Importa record ...",
            'fr': "Importer un enregistrement ...",
        },
        'Import completed successfully.': {
            'pl': "Import zakończony pomyślnie.",
            'es': "Importación completada con éxito.",
            'ru': "Импорт успешно завершён.",
            'de': "Import erfolgreich abgeschlossen.",
            'it': "Importazione completata con successo.",
            'fr': "Importation terminée avec succès.",
        },
        'Import failed': {
            'pl': "Import nie powiódł się",
            'es': "La importación falló",
            'ru': "Импорт не удался",
            'de': "Import fehlgeschlagen",
            'it': "Importazione fallita",
            'fr': "Échec de l'importation",
        },
        'Include hidden files/folders in scan.': {
            'pl': "Uwzględniaj pliki/foldery ukryte.",
            'es': "Incluir archivos/carpetas ocultos en el escaneo.",
            'ru': "Включить скрытые файлы/папки в сканирование.",
            'de': "Versteckte Dateien/Ordner in den Scan einbeziehen.",
            'it': "Includi file/cartelle nascosti nella scansione.",
            'fr': "Inclure les fichiers/dossiers cachés dans l'analyse.",
        },
        'Information': {
            'pl': "Informacja",
            'es': "Información",
            'ru': "Информация",
            'de': "Information",
            'it': "Informazione",
            'fr': "Information",
        },
        'Internal Label of the record to be created': {
            'pl': "Wewnętrzny identyfikator rekordu do utworzenia",
            'es': "Etiqueta interna del registro a crear",
            'ru': "Внутренний ярлык записи для создания",
            'de': "Interne Bezeichnung des zu erstellenden Datensatzes",
            'it': "Etichetta interna del record da creare",
            'fr': "Étiquette interne de l'enregistrement à créer",
        },
        "Keep 'Custom Data'": {
            'pl': "Zachowaj 'Dane Użytkownika'",
            'es': "Mantener 'Datos de Usuario'",
            'ru': "Сохранить 'Пользовательские данные'",
            'de': "'Benutzerdaten' behalten",
            'it': "Mantieni 'Dati Utente'",
            'fr': "Garder 'Données Utilisateur'",
        },
        'Label:': {
            'pl': "Nazwa:",
            'es': "Etiqueta:",
            'ru': "Метка:",
            'de': "Bezeichnung:",
            'it': "Etichetta:",
            'fr': "Étiquette :",
        },
        'Language Changed': {
            'pl': "Język został zmieniony",
            'es': "Idioma cambiado",
            'ru': "Язык изменён",
            'de': "Sprache geändert",
            'it': "Lingua cambiata",
            'fr': "Langue changée",
        },
        'Language:': {
            'pl': "Język:",
            'es': "Idioma:",
            'ru': "Язык:",
            'de': "Sprache:",
            'it': "Lingua:",
            'fr': "Langue :",
        },
        'License': {
            'pl': "Licencja",
            'es': "Licencia",
            'ru': "Лицензия",
            'de': "Lizenz",
            'it': "Licenza",
            'fr': "Licence",
        },
        'Loading errors': {
            'pl': "Błędy ładowania:",
            'es': "Errores de carga:",
            'ru': "Ошибки загрузки:",
            'de': "Ladefehler:",
            'it': "Errori di caricamento:",
            'fr': "Erreurs de chargement :",
        },
        'Loading records': {
            'pl': "Ładowanie rekordów:",
            'es': "Cargando registros:",
            'ru': "Загрузка записей:",
            'de': "Lade Datensätze:",
            'it': "Caricamento record:",
            'fr': "Chargement des enregistrements :",
        },
        'Loading records ...': {
            'pl': "Ładowanie rekordów ...",
            'es': "Cargando registros ...",
            'ru': "Загрузка записей ...",
            'de': "Lade Datensätze ...",
            'it': "Caricamento record ...",
            'fr': "Chargement des enregistrements ...",
        },
        'MASK_TOOLTIP': {
            'en': "Glob expressions separated by comma (',')\ne.g.: '*.7z, *.zip, *.gz'\n\nthe given executable will run\nwith every file matching the expression\n(and size criteria if provided)",
            'pl': "Wyrażenia 'glob' rozdzielone przecinkiem (',')\nnp.: '*.7z, *.zip, *.gz'\n\nPodany plik wykonywalny zostanie uruchomiony\nz każdym plikiem pasującym do wyrażenia\n(i kryteriów rozmiaru, jeśli zostały podane)",
            'es': "Expresiones 'glob' separadas por comas (',')\np.ej.: '*.7z, *.zip, *.gz'\n\nEl ejecutable dado se ejecutará\ncon cada archivo que coincida con la expresión\n(y los criterios de tamaño si se proporcionan)",
            'ru': "Выражения 'glob', разделённые запятой (',')\nнапример: '*.7z, *.zip, *.gz'\n\nДанный исполняемый файл будет запущен\nдля каждого файла, соответствующего выражению\n(и критериям размера, если они указаны)",
            'de': "'Glob'-Ausdrücke, getrennt durch Komma (',')\nz. B.: '*.7z, *.zip, *.gz'\n\nDie angegebene ausführbare Datei wird\nfür jede Datei ausgeführt, die dem Ausdruck entspricht\n(und den Größenkriterien, falls angegeben)",
            'it': "Espressioni 'glob' separate da virgole (',')\nEs.: '*.7z, *.zip, *.gz'\n\nIl file eseguibile specificato verrà eseguito\ncon ogni file che corrisponde all'espressione\n(e ai criteri di dimensione, se forniti)",
            'fr': "Expressions 'glob' séparées par des virgules (',')\np. ex. : '*.7z, *.zip, *.gz'\n\nLe fichier exécutable donné sera exécuté\navec chaque fichier correspondant à l'expression\n(et aux critères de taille, si fournis)",
        },
        'Mark to use CD Extractor': {
            'pl': "Zaznacz by użyć CD ekstraktora",
            'es': "Marcar para usar el extractor de CD",
            'ru': "Отметьте для использования CD Extractor",
            'de': "Markieren, um CD-Extractor zu verwenden",
            'it': "Seleziona per utilizzare il CD Extractor",
            'fr': "Marquer pour utiliser l'extracteur de CD",
        },
        'Max modtime': {
            'pl': "Maksymalny czas modyfikacji",
            'es': "Tiempo máximo de modificación",
            'ru': "Максимальное время изменения",
            'de': "Maximale Änderungszeit",
            'it': "Tempo massimo di modifica",
            'fr': "Temps de modification maximum",
        },
        'Max size': {
            'pl': "Maksymalna wielkość",
            'es': "Tamaño máximo",
            'ru': "Максимальный размер",
            'de': "Maximale Größe",
            'it': "Dimensione massima",
            'fr': "Taille maximale",
        },
        'Maximum file size': {
            'pl': "Maksymalna wielkość pliku",
            'es': "Tamaño máximo de archivo",
            'ru': "Максимальный размер файла",
            'de': "Maximale Dateigröße",
            'it': "Dimensione massima del file",
            'fr': "Taille maximale du fichier",
        },
        'Min modtime': {
            'pl': "Minimalny czas modyfikacji",
            'es': "Tiempo mínimo de modificación",
            'ru': "Минимальное время изменения",
            'de': "Minimale Änderungszeit",
            'it': "Tempo minimo di modifica",
            'fr': "Temps de modification minimum",
        },
        'Min size': {
            'pl': "Minimalna wielkość",
            'es': "Tamaño mínimo",
            'ru': "Минимальный размер",
            'de': "Minimale Größe",
            'it': "Dimensione minima",
            'fr': "Taille minimale",
        },
        'Minimum file size.': {
            'pl': "Minimalna wielkość pliku.",
            'es': "Tamaño mínimo de archivo.",
            'ru': "Минимальный размер файла.",
            'de': "Minimale Dateigröße.",
            'it': "Dimensione minima del file.",
            'fr': "Taille minimale du fichier.",
        },
        'Name': {
            'pl': 'Nazwa',
            'es': 'Nombre',
            'ru': 'Имя',
            'de': 'Name',
            'it': 'Nome',
            'fr': 'Nom',
        },
        "Navigate search results by\n'Find next (F3)' & 'Find prev (Shift+F3)'\nactions.": {
            'pl': "Przeglądaj wyniki wyszukiwania za pomocą akcji\n'Znajdź następny (F3)' i 'Znajdź poprzedni (Shift+F3)'.",
            'es': "Navegue por los resultados de búsqueda mediante las acciones\n'Buscar siguiente (F3)' y 'Buscar anterior (Shift+F3)'.",
            'ru': "Просматривайте результаты поиска с помощью действий\n'Найти далее (F3)' и 'Найти назад (Shift+F3)'.",
            'de': "Navigieren Sie durch Suchergebnisse mit den Aktionen\n'Weiter suchen (F3)' und 'Zurück suchen (Shift+F3)'.",
            'it': "Naviga tra i risultati di ricerca con le azioni\n'Trova successivo (F3)' e 'Trova precedente (Shift+F3)'.",
            'fr': "Naviguez dans les résultats de recherche avec les actions\n'Trouver suivant (F3)' et 'Trouver précédent (Shift+F3)'.",
        },
        'New Record ...': {
            'pl': 'Nowy Rekord ...',
            'es': 'Nuevo Registro ...',
            'ru': 'Новая запись ...',
            'de': 'Neuer Eintrag ...',
            'it': 'Nuovo Record ...',
            'fr': 'Nouvel Enregistrement ...',
        },
        'New alias name for record': {
            'pl': 'Nowy Alias:',
            'es': 'Nuevo alias:',
            'ru': 'Новое имя псевдонима:',
            'de': 'Neuer Aliasname:',
            'it': 'Nuovo alias:',
            'fr': 'Nouveau nom d\'alias:',
        },
        'New group': {
            'pl': 'Nowa grupa',
            'es': 'Nuevo grupo',
            'ru': 'Новая группа',
            'de': 'Neue Gruppe',
            'it': 'Nuovo gruppo',
            'fr': 'Nouveau groupe',
        },
        'New group ...': {
            'pl': 'Nowa grupa ...',
            'es': 'Nuevo grupo ...',
            'ru': 'Новая группа ...',
            'de': 'Neue Gruppe ...',
            'it': 'Nuovo gruppo ...',
            'fr': 'Nouveau groupe ...',
        },
        'New group name:': {
            'pl': 'Nazwa nowej grupy',
            'es': 'Nombre del nuevo grupo:',
            'ru': 'Имя новой группы:',
            'de': 'Name der neuen Gruppe:',
            'it': 'Nome del nuovo gruppo:',
            'fr': 'Nom du nouveau groupe:',
        },
        'No': {
            'pl': 'Nie',
            'es': 'No',
            'ru': 'Нет',
            'de': 'Nein',
            'it': 'No',
            'fr': 'Non',
        },
        'No CD extracted (empty value)': {
            'pl': 'Puste Dane Użytkownika',
            'es': 'Datos de Usuario Vacíos',
            'ru': 'Пустые данные пользователя',
            'de': 'Leere Benutzerdaten',
            'it': 'Dati Utente Vuoti',
            'fr': 'Données Utilisateur Vides',
        },
        'No Custom Data': {
            'pl': 'Brak Danych Użytkownika',
            'es': 'Sin Datos de Usuario',
            'ru': 'Нет данных пользователя',
            'de': 'Keine Benutzerdaten',
            'it': 'Nessun Dato Utente',
            'fr': 'Pas de Données Utilisateur',
        },
        'No Custom data.': {
            'pl': 'Brak Danych Użytkownika',
            'es': 'Sin Datos de Usuario.',
            'ru': 'Нет данных пользователя.',
            'de': 'Keine Benutzerdaten.',
            'it': 'Nessun Dato Utente.',
            'fr': 'Pas de Données Utilisateur.',
        },
        'No files / No folders': {
            'pl': 'Brak plików / Brak folderów',
            'es': 'No hay archivos / No hay carpetas',
            'ru': 'Нет файлов / Нет папок',
            'de': 'Keine Dateien / Keine Ordner',
            'it': 'Nessun file / Nessuna cartella',
            'fr': 'Aucun fichier / Aucun dossier',
        },
        'No files in records.': {
            'pl': 'Brak plików w rekordach',
            'es': 'No hay archivos en los registros.',
            'ru': 'Нет файлов в записях.',
            'de': 'Keine Dateien in den Einträgen.',
            'it': 'Nessun file nei record.',
            'fr': 'Aucun fichier dans les enregistrements.',
        },
        'No paths to scan.': {
            'pl': 'Brak ścieżek do skanowania',
            'es': 'No hay rutas para escanear.',
            'ru': 'Нет путей для сканирования.',
            'de': 'Keine Pfade zum Scannen.',
            'it': 'Nessun percorso da scansionare.',
            'fr': 'Aucun chemin à scanner.',
        },
        'No records.': {
            'pl': 'Brak rekordów',
            'es': 'No hay registros.',
            'ru': 'Нет записей.',
            'de': 'Keine Einträge.',
            'it': 'Nessun record.',
            'fr': 'Aucun enregistrement.',
        },
        'No search results\nClick to open find dialog.': {
            'pl': 'Brak wyników wyszukiwania\nKliknij by otworzyć dialog wyszukiwania.',
            'es': 'Sin resultados de búsqueda\nHaz clic para abrir el cuadro de búsqueda.',
            'ru': 'Нет результатов поиска\nНажмите, чтобы открыть диалог поиска.',
            'de': 'Keine Suchergebnisse\nKlicken Sie, um den Suchdialog zu öffnen.',
            'it': 'Nessun risultato di ricerca\nClicca per aprire il dialogo di ricerca.',
            'fr': 'Aucun résultat de recherche\nCliquez pour ouvrir la boîte de dialogue de recherche.',
        },
        'Number of threads used to extract Custom Data\n\n0 - all available CPU cores\n1 - single thread (default value)\n\nThe optimal value depends on the CPU cores performace,\nIO subsystem performance and Custom Data Extractor specifics.\n\nConsider limitations of parallel CDE execution e.g.\nnumber of licenses of used software,\nused working directory, needed memory etc.': {
            'pl': 'Liczba wątków użytych do wyodrębnienia danych użytkownika\n\n0 - wszystkie dostępne rdzenie procesora\n1 - pojedynczy wątek (wartość domyślna)\n\nWartość optymalna zależy od wydajności rdzeni procesora,\nwydajności podsystemu wejścia/wyjścia i specyfiki programu Custom Data Extractor.\n\nNależy wziąć pod uwagę ograniczenia równoległego wykonywania CDE, np.\nliczbę licencji używanego oprogramowania,\nużywany katalog roboczy, potrzebną pamięć itp.',
            'es': 'Número de hilos utilizados para extraer Datos de Usuario\n\n0 - todos los núcleos de CPU disponibles\n1 - un solo hilo (valor predeterminado)\n\nEl valor óptimo depende del rendimiento de los núcleos de la CPU,\ndel rendimiento del subsistema de E/S y de las especificaciones del Extractor de Datos de Usuario.\n\nConsidere las limitaciones de la ejecución paralela de CDE, p. ej.\nnúmero de licencias del software utilizado,\ndirectorio de trabajo utilizado, memoria necesaria, etc.',
            'ru': 'Количество потоков, используемых для извлечения данных пользователя\n\n0 - все доступные ядра процессора\n1 - один поток (значение по умолчанию)\n\nОптимальное значение зависит от производительности ядер процессора,\nпроизводительности подсистемы ввода-вывода и специфики Extractor Custom Data.\n\nУчитывайте ограничения параллельного выполнения CDE, например\nчисло лицензий используемого программного обеспечения,\nиспользуемый рабочий каталог, необходимую память и т. д.',
            'de': 'Anzahl der Threads, die zur Extraktion von Benutzerdaten verwendet werden\n\n0 - alle verfügbaren CPU-Kerne\n1 - ein Thread (Standardwert)\n\nDer optimale Wert hängt von der Leistung der CPU-Kerne,\nder Leistung des E/A-Subsystems und den Spezifikationen des Custom Data Extractor ab.\n\nBerücksichtigen Sie Einschränkungen bei der parallelen Ausführung von CDE, z. B.\nAnzahl der Lizenzen der verwendeten Software,\nverwendetes Arbeitsverzeichnis, benötigter Speicher usw.',
            'it': 'Numero di thread utilizzati per estrarre i Dati Utente\n\n0 - tutti i core della CPU disponibili\n1 - un singolo thread (valore predefinito)\n\nIl valore ottimale dipende dalle prestazioni dei core della CPU,\ndalle prestazioni del sottosistema I/O e dalle specifiche del Custom Data Extractor.\n\nConsiderare le limitazioni dell\'esecuzione parallela di CDE, ad es.\nnumero di licenze del software utilizzato,\ndirectory di lavoro utilizzata, memoria necessaria, ecc.',
            'fr': 'Nombre de threads utilisés pour extraire les Données Utilisateur\n\n0 - tous les cœurs de processeur disponibles\n1 - un seul thread (valeur par défaut)\n\nLa valeur optimale dépend des performances des cœurs du processeur,\ndes performances du sous-système E/S et des spécifications de l\'Extracteur de Données Utilisateur.\n\nPrenez en compte les limitations de l\'exécution parallèle de CDE, par exemple\nle nombre de licences du logiciel utilisé,\nle répertoire de travail utilisé, la mémoire nécessaire, etc.',
        },
        'OPEN_TOOLTIP': {
            'en': 'Choose the executable file to serve as a custom data extractor...',
            'pl': 'Wybierz plik wykonywalny, który będzie służył jako ekstraktor Danych Użytkownika...',
            'es': 'Elija el archivo ejecutable para servir como extractor de Datos de Usuario...',
            'ru': 'Выберите исполняемый файл, который будет служить экстрактором данных пользователя...',
            'de': 'Wählen Sie die ausführbare Datei, die als Benutzerdaten-Extraktor dient...',
            'it': 'Scegli il file eseguibile da utilizzare come estrattore di Dati Utente...',
            'fr': 'Choisissez le fichier exécutable pour servir d\'extracteur de Données Utilisateur...',
        },
        'Open current Log': {
            'pl': 'Otwórz log',
            'es': 'Abrir registro actual',
            'ru': 'Открыть текущий журнал',
            'de': 'Aktuelles Protokoll öffnen',
            'it': 'Apri il registro corrente',
            'fr': 'Ouvrir le journal actuel',
        },
        'Open homepage': {
            'pl': 'Otwórz stronę domową',
            'es': 'Abrir página de inicio',
            'ru': 'Открыть домашнюю страницу',
            'de': 'Startseite öffnen',
            'it': 'Apri la pagina iniziale',
            'fr': 'Ouvrir la page d\'accueil',
        },
        'Open logs directory': {
            'pl': 'Otwórz katalog z logami',
            'es': 'Abrir directorio de registros',
            'ru': 'Открыть каталог журналов',
            'de': 'Protokollverzeichnis öffnen',
            'it': 'Apri la directory dei log',
            'fr': 'Ouvrir le répertoire des journaux',
        },
        'Opening dialog ...': {
            'pl': 'Otwieranie dialogu ...',
            'es': 'Abriendo diálogo ...',
            'ru': 'Открытие диалога ...',
            'de': 'Dialog wird geöffnet ...',
            'it': 'Apertura del dialogo ...',
            'fr': 'Ouverture de la boîte de dialogue ...',
        },
        'Options': {
            'pl': 'Opcje',
            'es': 'Opciones',
            'ru': 'Параметры',
            'de': 'Optionen',
            'it': 'Opzioni',
            'fr': 'Options',
        },
        'PARS_TOOLTIP': {
            'en': "The executable will run with the full path to the file to extract as a parameter.\nIf other constant parameters are necessary, they should be placed here\nand the scanned file should be indicated with the '%' sign.\nThe absence of the '%' sign means that the file will be passed as the last parameter.\ne.g.:const_param % other_const_param",
            'pl': "Plik wykonywalny zostanie uruchomiony z pełną ścieżką do pliku do wyodrębnienia jako parametrem.\nJeśli wymagane są inne stałe parametry, należy je umieścić tutaj\na skanowany plik należy oznaczyć znakiem '%'.\nBrak znaku '%' oznacza, że \u200b\u200bplik zostanie przekazany jako ostatni parametr.\ne.g.:const_param % other_const_param",
            'es': "El ejecutable se ejecutará con la ruta completa del archivo a extraer como parámetro.\nSi se necesitan otros parámetros constantes, deben colocarse aquí\ny el archivo escaneado debe indicarse con el signo '%'.\nLa ausencia del signo '%' significa que el archivo se pasará como último parámetro.\ne.g.:const_param % other_const_param",
            'ru': "Исполняемый файл будет запущен с полным путем к файлу для извлечения в качестве параметра.\nЕсли необходимы другие постоянные параметры, их следует указать здесь,\nа сканируемый файл должен быть обозначен знаком '%'.\nОтсутствие знака '%' означает, что файл будет передан как последний параметр.\ne.g.:const_param % other_const_param",
            'de': "Die ausführbare Datei wird mit dem vollständigen Pfad zur extrahierenden Datei als Parameter ausgeführt.\nWenn andere konstante Parameter erforderlich sind, sollten sie hier platziert werden,\nund die zu scannende Datei sollte mit dem Zeichen '%' angegeben werden.\nDas Fehlen des Zeichens '%' bedeutet, dass die Datei als letzter Parameter übergeben wird.\ne.g.:const_param % other_const_param",
            'it': "L'eseguibile verrà eseguito con il percorso completo del file da estrarre come parametro.\nSe sono necessari altri parametri costanti, devono essere inseriti qui\ne il file scansionato deve essere indicato con il segno '%'.\nL'assenza del segno '%' significa che il file verrà passato come ultimo parametro.\ne.g.:const_param % other_const_param",
            'fr': "L'exécutable sera exécuté avec le chemin complet vers le fichier à extraire en tant que paramètre.\nSi d'autres paramètres constants sont nécessaires, ils doivent être placés ici,\net le fichier analysé doit être indiqué par le signe '%'.\nL'absence du signe '%' signifie que le fichier sera passé en dernier paramètre.\ne.g.:const_param % other_const_param"
        },
        'Parameters': {
            'pl': 'Parametry',
            'es': 'Parámetros',
            'ru': 'Параметры',
            'de': 'Parameter',
            'it': 'Parametri',
            'fr': 'Paramètres'
        },
        'Parsing WII files ... ': {
            'pl': 'Parsowanie pliku WII',
            'es': 'Analizando archivos WII...',
            'ru': 'Анализ файлов WII...',
            'de': 'WII-Dateien werden analysiert...',
            'it': 'Analisi dei file WII...',
            'fr': 'Analyse des fichiers WII...'
        },
        'Parsing file(s)': {
            'pl': 'Parsowanie pliku/plików',
            'es': 'Analizando archivo(s)',
            'ru': 'Анализ файла(ов)',
            'de': 'Datei(en) werden analysiert',
            'it': 'Analisi del/dei file',
            'fr': 'Analyse du/des fichier(s)'
        },
        'Path does not exist': {
            'pl': 'Ścieżka nie istnieje',
            'es': 'La ruta no existe',
            'ru': 'Путь не существует',
            'de': 'Pfad existiert nicht',
            'it': 'Il percorso non esiste',
            'fr': 'Le chemin n\'existe pas'
        },
        'Path elements': {
            'pl': 'Elementy Ścieżki',
            'es': 'Elementos de la ruta',
            'ru': 'Элементы пути',
            'de': 'Pfadelemente',
            'it': 'Elementi del percorso',
            'fr': 'Éléments du chemin'
        },
        'Path to scan': {
            'pl': 'Ścieżka do skanowania',
            'es': 'Ruta para escanear',
            'ru': 'Путь для сканирования',
            'de': 'Pfad zum Scannen',
            'it': 'Percorso da analizzare',
            'fr': 'Chemin à analyser'
        },
        'Path:': {
            'pl': 'Ścieżka:',
            'es': 'Ruta:',
            'ru': 'Путь:',
            'de': 'Pfad:',
            'it': 'Percorso:',
            'fr': 'Chemin:'
        },
        'Proceed': {
            'pl': 'Kontynuuj',
            'es': 'Continuar',
            'ru': 'Продолжить',
            'de': 'Fortfahren',
            'it': 'Procedere',
            'fr': 'Continuer'
        },
        'Ready': {
            'pl': 'Gotowy',
            'es': 'Listo',
            'ru': 'Готово',
            'de': 'Bereit',
            'it': 'Pronto',
            'fr': 'Prêt'
        },
        'Record Info': {
            'pl': 'Informacje o rekordzie',
            'es': 'Información del registro',
            'ru': 'Информация о записи',
            'de': 'Aufzeichnungsinfo',
            'it': 'Informazioni sul record',
            'fr': 'Informations sur l\'enregistrement'
        },
        'Record Info ...': {
            'pl': 'Informacje o rekordzie ...',
            'es': 'Información del registro...',
            'ru': 'Информация о записи...',
            'de': 'Aufzeichnungsinfo...',
            'it': 'Informazioni sul record...',
            'fr': 'Informations sur l\'enregistrement...'
        },
        'Record Label': {
            'pl': 'Identyfikator Rekordu',
            'es': 'Etiqueta del registro',
            'ru': 'Метка записи',
            'de': 'Aufzeichnungsetikett',
            'it': 'Etichetta del record',
            'fr': 'Étiquette de l\'enregistrement'
        },
        'Records': {
            'pl': 'Rekordy',
            'es': 'Registros',
            'ru': 'Записи',
            'de': 'Aufzeichnungen',
            'it': 'Record',
            'fr': 'Enregistrements'
        },
        'Records in repository  ': {
            'pl': 'Rekordów w repozytorium    ',
            'es': 'Registros en el repositorio',
            'ru': 'Записей в репозитории',
            'de': 'Aufzeichnungen im Repository',
            'it': 'Record nel repository',
            'fr': 'Enregistrements dans le dépôt'
        },
        'Records loading aborted': {
            'pl': 'Ładowanie rekordów przerwane',
            'es': 'Carga de registros abortada',
            'ru': 'Загрузка записей прервана',
            'de': 'Laden der Aufzeichnungen abgebrochen',
            'it': 'Caricamento dei record interrotto',
            'fr': 'Chargement des enregistrements annulé'
        },
        'Records number:': {
            'pl': 'Ilość rekordów:',
            'es': 'Número de registros:',
            'ru': 'Количество записей:',
            'de': 'Anzahl der Aufzeichnungen:',
            'it': 'Numero di record:',
            'fr': 'Nombre d\'enregistrements:'
        },
        'Records space:': {
            'pl': 'Zajętość rekordów:',
            'es': 'Espacio de registros:',
            'ru': 'Место для записей:',
            'de': 'Aufzeichnungsspeicher:',
            'it': 'Spazio dei record:',
            'fr': 'Espace des enregistrements:'
        },
        'Regular expression': {
            'pl': 'Wyrażenie regularne',
            'es': 'Expresión regular',
            'ru': 'Регулярное выражение',
            'de': 'Regulärer Ausdruck',
            'it': 'Espressione regolare',
            'fr': 'Expression régulière'
        },
        'Regular expression on Custom Data': {
            'pl': 'Wyrażenie regularne na Danych Użytkownika',
            'es': 'Expresión regular en Datos del Usuario',
            'ru': 'Регулярное выражение для пользовательских данных',
            'de': 'Regulärer Ausdruck auf Benutzerdaten',
            'it': 'Espressione regolare sui Dati Utente',
            'fr': 'Expression régulière sur les Données Utilisateur'
        },
        'Regular expression on path element': {
            'pl': 'Wyrażenie regularne na elemencie ścieżki',
            'es': 'Expresión regular en elemento de ruta',
            'ru': 'Регулярное выражение для элемента пути',
            'de': 'Regulärer Ausdruck auf Pfadelement',
            'it': 'Espressione regolare su elemento del percorso',
            'fr': 'Expression régulière sur l\'élément de chemin'
        },
        'Remove group ...': {
            'pl': 'Usuń grupę ...',
            'es': 'Eliminar grupo ...',
            'ru': 'Удалить группу ...',
            'de': 'Gruppe entfernen ...',
            'it': 'Rimuovi gruppo ...',
            'fr': 'Supprimer le groupe ...'
        },
        'Remove record from group ...': {
            'pl': 'Usuń rekord z grupy ...',
            'es': 'Eliminar registro del grupo ...',
            'ru': 'Удалить запись из группы ...',
            'de': 'Aufzeichnung aus Gruppe entfernen ...',
            'it': 'Rimuovi record dal gruppo ...',
            'fr': 'Supprimer l\'enregistrement du groupe ...'
        },
        'Rename / Alias name ...': {
            'pl': 'Zmień nazwę / Utwórz alias ...',
            'es': 'Renombrar / Crear alias ...',
            'ru': 'Переименовать / Создать псевдоним ...',
            'de': 'Umbenennen / Alias erstellen ...',
            'it': 'Rinomina / Crea alias ...',
            'fr': 'Renommer / Créer un alias ...'
        },
        'Rename / Repack ...': {
            'pl': 'Zmień nazwę / Przepakuj ...',
            'es': 'Renombrar / Reempaquetar ...',
            'ru': 'Переименовать / Перепаковать ...',
            'de': 'Umbenennen / Neu packen ...',
            'it': 'Rinomina / Reimpacchetta ...',
            'fr': 'Renommer / Réempaqueter ...'
        },
        'Rename / Repack record': {
            'pl': 'Zmień nazwę / Przepakuj',
            'es': 'Renombrar / Reempaquetar registro',
            'ru': 'Переименовать / Перепаковать запись',
            'de': 'Aufzeichnung umbenennen / Neu packen',
            'it': 'Rinomina / Reimpacchetta record',
            'fr': 'Renommer / Réempaqueter l\'enregistrement'
        },
        'Rename failed.': {
            'pl': 'Zmiana nazwy nie powiodła się.',
            'es': 'Error al renombrar.',
            'ru': 'Ошибка переименования.',
            'de': 'Umbenennung fehlgeschlagen.',
            'it': 'Rinomina fallita.',
            'fr': 'Échec du renommage.'
        },
        'Rename group': {
            'pl': 'Zmień nazwę grupy',
            'es': 'Renombrar grupo',
            'ru': 'Переименовать группу',
            'de': 'Gruppe umbenennen',
            'it': 'Rinomina gruppo',
            'fr': 'Renommer le groupe'
        },
        'Repacking failed': {
            'pl': 'Przepakowaniwe nie powiodło się',
            'es': 'Error al reempaquetar',
            'ru': 'Ошибка перепаковки',
            'de': 'Neu packen fehlgeschlagen',
            'it': 'Reimpacchettamento fallito',
            'fr': 'Échec du réempaquetage'
        },
        'Repacking finished.': {
            'pl': 'Przepakowaniwe zakończone.',
            'es': 'Reempaquetado terminado.',
            'ru': 'Перепаковка завершена.',
            'de': 'Neu packen abgeschlossen.',
            'it': 'Reimpacchettamento completato.',
            'fr': 'Réempaquetage terminé.'
        },
        'Restart Librer to gain full access to the recordset.': {
            'pl': 'Uruchom ponownie Librera by uzyskać pełny dostęp do rekordów.',
            'es': 'Reinicie Librer para obtener acceso completo al conjunto de registros.',
            'ru': 'Перезапустите Librer, чтобы получить полный доступ к набору записей.',
            'de': 'Starten Sie Librer neu, um vollen Zugriff auf den Datensatz zu erhalten.',
            'it': 'Riavvia Librer per ottenere pieno accesso al set di record.',
            'fr': 'Redémarrez Librer pour obtenir un accès complet à l\'ensemble des enregistrements.'
        },
        'SHELL_TOOLTIP': {
            'en': 'Execute in the system shell.\n\nWhen enabled\nCommand with parameters will be passed\nto the system shell as single string\nThe use of pipes, redirection etc. is allowed.\nUsing of quotes (") may be necessary. Scanned\nfiles will be automatically enclosed with quotation marks.\nExample:\n{shell_example}\n\nWhen disabled\nAn executable file must be specified,\nthe contents of the parameters field will be\nsplitted and passed as a parameters list.\n\nIn more complicated cases\nit is recommended to prepare a dedicated shell\nscript and use it as a shell command.',
            'pl': 'Wykonaj w powłoce systemowej.\n\nPo włączeniu\nPolecenie z parametrami zostanie przekazane\ndo powłoki systemowej jako pojedynczy ciąg\nDozwolone jest używanie potoków, przekierowań itp.\nMoże być konieczne użycie cudzysłowów ("). Przeskanowane\npliki zostaną automatycznie ujęte w cudzysłowy.\nPrzykład:\n{shell_example}\n\nPo wyłączeniu\nNależy określić plik wykonywalny,\nzawartość pola parametrów zostanie\npodzielona i przekazana jako lista parametrów.\n\nW bardziej skomplikowanych przypadkach\nzaleca się przygotowanie dedykowanego skryptu powłoki i\nużycie go jako polecenia powłoki.',
            'es': 'Ejecutar en el shell del sistema.\n\nCuando esté habilitado\nEl comando con parámetros se pasará\nal shell del sistema como una sola cadena\nSe permite el uso de pipes, redirección, etc.\nEl uso de comillas (") puede ser necesario. Los archivos\nescanneados se encerrarán automáticamente entre comillas.\nEjemplo:\n{shell_example}\n\nCuando esté deshabilitado\nSe debe especificar un archivo ejecutable,\nlos contenidos del campo de parámetros se\nsepararán y se pasarán como una lista de parámetros.\n\nEn casos más complicados\nse recomienda preparar un script de shell dedicado\ny usarlo como comando de shell.',
            'ru': 'Выполнить в системной оболочке.\n\nКогда включено\nКоманда с параметрами будет передана\nв системную оболочку как одна строка.\nДопускается использование конвейеров, перенаправлений и т.д.\nМожет потребоваться использование кавычек ("). Отсканированные\nфайлы будут автоматически заключены в кавычки.\nПример:\n{shell_example}\n\nКогда выключено\nНеобходимо указать исполнимый файл,\nсодержимое поля параметров будет\nразделено и передано как список параметров.\n\nВ более сложных случаях\nрекомендуется подготовить отдельный скрипт оболочки\nи использовать его как команду оболочки.',
            'de': 'Im System-Shell ausführen.\n\nWenn aktiviert\nWird der Befehl mit Parametern\nals einzelner String an die Shell übergeben.\nDie Verwendung von Pipes, Umleitungen usw. ist erlaubt.\nEs kann notwendig sein, Anführungszeichen (") zu verwenden. Gescannte\nDateien werden automatisch in Anführungszeichen gesetzt.\nBeispiel:\n{shell_example}\n\nWenn deaktiviert\nMuss eine ausführbare Datei angegeben werden,\ndie Inhalte des Parameterfeldes werden\ngesplittet und als Parameterliste übergeben.\n\nIn komplizierteren Fällen\nwird empfohlen, ein dediziertes Shell-Skript vorzubereiten\nund es als Shell-Befehl zu verwenden.',
            'it': 'Esegui nella shell di sistema.\n\nQuando abilitato\nIl comando con i parametri verrà passato\nalla shell di sistema come una singola stringa.\nÈ consentito l\'uso di pipe, reindirizzamenti, ecc.\nPotrebbe essere necessario usare virgolette ("). I file\nscansionati verranno automaticamente racchiusi tra virgolette.\nEsempio:\n{shell_example}\n\nQuando disabilitato\nDeve essere specificato un file eseguibile,\nil contenuto del campo parametri verrà\ndiviso e passato come lista di parametri.\n\nNei casi più complicati\nsi consiglia di preparare uno script shell dedicato\ne utilizzarlo come comando shell.',
            'fr': 'Exécuter dans le shell système.\n\nLorsque activé\nLa commande avec paramètres sera passée\nau shell système sous forme d\'une seule chaîne.\nL\'utilisation de tuyaux, redirections, etc. est autorisée.\nL\'utilisation de guillemets (") peut être nécessaire. Les fichiers\nanalysés seront automatiquement entourés de guillemets.\nExemple :\n{shell_example}\n\nLorsque désactivé\nUn fichier exécutable doit être spécifié,\nle contenu du champ paramètres sera\nséparé et passé sous forme de liste de paramètres.\n\nDans des cas plus compliqués\nil est recommandé de préparer un script shell dédié\net de l\'utiliser comme commande shell.'
        },
        'SIZE_TOOLTIP': {
            'en': 'Integer value [in bytes] or integer with unit.\nLeave the value blank to ignore this criterion.\n\nexamples:\n399\n100B\n125kB\n10MB',
            'pl': 'Wartość całkowita [w bajtach] lub liczba całkowita z jednostką.\nPozostaw wartość pustą, aby zignorować to kryterium.\n\nPrzykłady:\n399\n100B\n125kB\n10MB',
            'es': 'Valor entero [en bytes] o valor entero con unidad.\nDeja el valor en blanco para ignorar este criterio.\n\nEjemplos:\n399\n100B\n125kB\n10MB',
            'ru': 'Целое число [в байтах] или целое число с единицей.\nОставьте значение пустым, чтобы игнорировать этот критерий.\n\nПримеры:\n399\n100B\n125kB\n10MB',
            'de': 'Ganzzahlwert [in Bytes] oder Ganzzahl mit Einheit.\nLassen Sie den Wert leer, um dieses Kriterium zu ignorieren.\n\nBeispiele:\n399\n100B\n125kB\n10MB',
            'it': 'Valore intero [in byte] o valore intero con unità.\nLascia il valore vuoto per ignorare questo criterio.\n\nEsempi:\n399\n100B\n125kB\n10MB',
            'fr': 'Valeur entière [en octets] ou valeur entière avec unité.\nLaissez la valeur vide pour ignorer ce critère.\n\nExemples:\n399\n100B\n125kB\n10MB'
        },
        'Save results': {
            'pl': 'Zapisz wyniki',
            'es': 'Guardar resultados',
            'ru': 'Сохранить результаты',
            'de': 'Ergebnisse speichern',
            'it': 'Salva i risultati',
            'fr': 'Sauvegarder les résultats'
        },
        'Scan': {
            'pl': 'Skanuj',
            'es': 'Escanear',
            'ru': 'Сканировать',
            'de': 'Scannen',
            'it': 'Scansiona',
            'fr': 'Scanner'
        },
        'Search': {
            'pl': 'Szukaj',
            'es': 'Buscar',
            'ru': 'Поиск',
            'de': 'Suchen',
            'it': 'Cerca',
            'fr': 'Rechercher'
        },
        'Search aborted.': {
            'pl': 'Wyszukiwanie przerwane.',
            'es': 'Búsqueda abortada.',
            'ru': 'Поиск прерван.',
            'de': 'Suche abgebrochen.',
            'it': 'Ricerca interrotta.',
            'fr': 'Recherche annulée.'
        },
        'Search in': {
            'pl': 'Poszukiwanie w:',
            'es': 'Buscar en:',
            'ru': 'Поиск в:',
            'de': 'Suche in:',
            'it': 'Cerca in:',
            'fr': 'Rechercher dans:'
        },
        'Search in all records': {
            'pl': 'Szukaj we wszystkich rekordach',
            'es': 'Buscar en todos los registros',
            'ru': 'Поиск во всех записях',
            'de': 'In allen Datensätzen suchen',
            'it': 'Cerca in tutti i record',
            'fr': 'Rechercher dans tous les enregistrements'
        },
        'Search progress': {
            'pl': 'Postęp wyszukiwania',
            'es': 'Progreso de búsqueda',
            'ru': 'Прогресс поиска',
            'de': 'Suchfortschritt',
            'it': 'Progresso della ricerca',
            'fr': 'Progrès de la recherche'
        },
        'Search range': {
            'pl': 'Zakres przeszukiwania',
            'es': 'Rango de búsqueda',
            'ru': 'Диапазон поиска',
            'de': 'Suchbereich',
            'it': 'Intervallo di ricerca',
            'fr': 'Plage de recherche'
        },
        'Search records': {
            'pl': 'Przeszukaj rekordy',
            'es': 'Buscar registros',
            'ru': 'Искать записи',
            'de': 'Datensätze durchsuchen',
            'it': 'Cerca nei record',
            'fr': 'Rechercher des enregistrements'
        },
        'Search results': {
            'pl': 'Wyniki wyszukiwania',
            'es': 'Resultados de búsqueda',
            'ru': 'Результаты поиска',
            'de': 'Suchergebnisse',
            'it': 'Risultati della ricerca',
            'fr': 'Résultats de la recherche'
        },
        'Searching aborted. Results may be incomplete.': {
            'pl': 'Przeszukiwanie przerwane. Wyniki mogą być niekompletne.',
            'es': 'Búsqueda abortada. Los resultados pueden estar incompletos.',
            'ru': 'Поиск прерван. Результаты могут быть неполными.',
            'de': 'Suche abgebrochen. Ergebnisse können unvollständig sein.',
            'it': 'Ricerca interrotta. I risultati potrebbero essere incompleti.',
            'fr': 'Recherche annulée. Les résultats peuvent être incomplets.'
        },
        'Select Directory': {
            'pl': 'Wybierz katalog',
            'es': 'Seleccionar directorio',
            'ru': 'Выбрать каталог',
            'de': 'Verzeichnis auswählen',
            'it': 'Seleziona directory',
            'fr': 'Sélectionner le répertoire'
        },
        'Select File': {
            'pl': 'Wybierz plik',
            'es': 'Seleccionar archivo',
            'ru': 'Выбрать файл',
            'de': 'Datei auswählen',
            'it': 'Seleziona file',
            'fr': 'Sélectionner le fichier'
        },
        'Select Next': {
            'pl': 'Wybierz następny',
            'es': 'Seleccionar siguiente',
            'ru': 'Выбрать следующий',
            'de': 'Nächsten auswählen',
            'it': 'Seleziona successivo',
            'fr': 'Sélectionner suivant'
        },
        'Select Prev': {
            'pl': 'Wybierz poprzedni',
            'es': 'Seleccionar anterior',
            'ru': 'Выбрать предыдущий',
            'de': 'Vorheriges auswählen',
            'it': 'Seleziona precedente',
            'fr': 'Sélectionner précédent'
        },
        'Select device to scan.': {
            'pl': 'Wybierz urządzenie do skanowania.',
            'es': 'Seleccionar dispositivo para escanear.',
            'ru': 'Выберите устройство для сканирования.',
            'de': 'Gerät zum Scannen auswählen.',
            'it': 'Seleziona dispositivo da scansionare.',
            'fr': 'Sélectionner un appareil à scanner.'
        },
        'Selected record / group': {
            'pl': 'Wybrany rekord / grupa',
            'es': 'Registro / grupo seleccionado',
            'ru': 'Выбранная запись / группа',
            'de': 'Ausgewählter Datensatz / Gruppe',
            'it': 'Record / gruppo selezionato',
            'fr': 'Enregistrement / groupe sélectionné'
        },
        'Set path to scan.': {
            'pl': 'Ustaw ścieżkę do skanowania.',
            'es': 'Establecer la ruta para escanear.',
            'ru': 'Установить путь для сканирования.',
            'de': 'Pfad zum Scannen festlegen.',
            'it': 'Imposta il percorso da scansionare.',
            'fr': 'Définir le chemin à scanner.'
        },
        'Settings': {
            'pl': 'Ustawienia',
            'es': 'Configuraciones',
            'ru': 'Настройки',
            'de': 'Einstellungen',
            'it': 'Impostazioni',
            'fr': 'Paramètres'
        },
        'Settings ...': {
            'pl': 'Ustawienia',
            'es': 'Configuraciones...',
            'ru': 'Настройки...',
            'de': 'Einstellungen...',
            'it': 'Impostazioni...',
            'fr': 'Paramètres...'
        },
        'Show Custom Data ...': {
            'pl': 'Pokaż Dane Użytkownika ...',
            'es': 'Mostrar Datos del Usuario ...',
            'ru': 'Показать данные пользователя ...',
            'de': 'Benutzerdaten anzeigen ...',
            'it': 'Mostra Dati utente ...',
            'fr': 'Afficher les données utilisateur ...'
        },
        'Show results': {
            'pl': 'Pokaż wyniki',
            'es': 'Mostrar resultados',
            'ru': 'Показать результаты',
            'de': 'Ergebnisse anzeigen',
            'it': 'Mostra risultati',
            'fr': 'Afficher les résultats'
        },
        'Show tooltips': {
            'pl': 'Pokaż dymki z podpowiedziami',
            'es': 'Mostrar descripciones emergentes',
            'ru': 'Показать подсказки',
            'de': 'Tooltips anzeigen',
            'it': 'Mostra suggerimenti',
            'fr': 'Afficher les info-bulles'
        },
        'Size': {
            'pl': 'Wielkość',
            'es': 'Tamaño',
            'ru': 'Размер',
            'de': 'Größe',
            'it': 'Dimensione',
            'fr': 'Taille'
        },
        'Start scanning.\n\nIf any Custom Data Extractor is enabled it will be executed\nwith every file that meets its criteria (mask & size).': {
            'pl': 'Rozpocznij skanowanie.\n\nJeśli włączony jest dowolny Ekstraktor Danych, zostanie on uruchomiony\nz każdym plikiem spełniającym jego kryteria (maska i rozmiar)',
            'es': 'Iniciar escaneo.\n\nSi algún extractor de datos del usuario está habilitado, se ejecutará\ncon cada archivo que cumpla con sus criterios (máscara y tamaño).',
            'ru': 'Начать сканирование.\n\nЕсли включен любой экстрактор данных пользователя, он будет выполнен\nс каждым файлом, который соответствует его критериям (маска и размер).',
            'de': 'Scannen starten.\n\nWenn ein benutzerdefinierter Datenextraktor aktiviert ist, wird er ausgeführt\nmit jeder Datei, die seinen Kriterien (Maske und Größe) entspricht.',
            'it': 'Avvia scansione.\n\nSe è attivato un estrattore di dati utente, verrà eseguito\ncon ogni file che soddisfa i suoi criteri (maschera e dimensione).',
            'fr': 'Démarrer l\'analyse.\n\nSi un extracteur de données utilisateur est activé, il sera exécuté\navec chaque fichier qui respecte ses critères (masque et taille).'
        },
        'Sum data size         ': {
            'pl': 'Sumaryczna ilość danych    ',
            'es': 'Tamaño total de datos    ',
            'ru': 'Общий размер данных    ',
            'de': 'Gesamtgröße der Daten    ',
            'it': 'Dimensione totale dei dati    ',
            'fr': 'Taille totale des données    '
        },
        'Sum files quantity    ': {
            'pl': 'Sumaryczna ilość plików    ',
            'es': 'Cantidad total de archivos    ',
            'ru': 'Общее количество файлов    ',
            'de': 'Gesamtanzahl der Dateien    ',
            'it': 'Quantità totale di file    ',
            'fr': 'Quantité totale de fichiers    '
        },
        'Symlink': {
            'pl': 'Powiązanie symboliczne',
            'es': 'Enlace simbólico',
            'ru': 'Символическая ссылка',
            'de': 'Symbolischer Link',
            'it': 'Collegamento simbolico',
            'fr': 'Lien symbolique'
        },
        'TEST_TOOLTIP':{
            'en': 'Select a file and test your Custom Data Extractor.\n\n',
            'pl': 'Wybierz plik i przetestuj swój niestandardowy ekstraktor danych.\n\n',
            'es': 'Seleccione un archivo y pruebe su extractor de datos personalizados.\n\n',
            'ru': 'Выберите файл и протестируйте свой извлекатель пользовательских данных.\n\n',
            'de': 'Wählen Sie eine Datei aus und testen Sie Ihren benutzerdefinierten Datenauszug.\n\n',
            'it': 'Seleziona un file e prova il tuo estrattore di dati personalizzati.\n\n',
            'fr': 'Sélectionnez un fichier et testez votre extracteur de données personnalisées.\n\n',
        },
        'TEST_TOOLTIP_COMMOMN':{
            'en': "Before you run scan, and therefore run your CDE on all\nfiles that will match on the scan path,\ntest your Custom Data Extractor\non a single, manually selected file.\nCheck if it's getting the expected data\nand has no unexpected side-effects.",
            'pl': 'Zanim uruchomisz skanowanie, a zatem uruchomisz CDE na wszystkich\nplikach, które będą pasować do ścieżki skanowania,\nprzetestuj swój niestandardowy ekstraktor danych\nna pojedynczym, ręcznie wybranym pliku.\nSprawdź, czy pobiera oczekiwane dane\ni czy nie ma nieoczekiwanych efektów ubocznych.',
            'es': "Antes de ejecutar el escaneo, y por lo tanto ejecutar su extractor de datos personalizados en todos\nlos archivos que coincidan con la ruta de escaneo,\ntestee su extractor de datos personalizados\nen un solo archivo seleccionado manualmente.\nVerifique si está obteniendo los datos esperados\ny si no tiene efectos secundarios inesperados.",
            'ru': "Перед запуском сканирования и, следовательно, перед запуском извлекателя пользовательских данных на всех\nфайлах, которые соответствуют пути сканирования,\nпроверьте свой извлекатель пользовательских данных\nна одном вручную выбранном файле.\nПроверьте, получает ли он ожидаемые данные\nи нет ли неожиданных побочных эффектов.",
            'de': "Bevor Sie den Scan durchführen und damit Ihren benutzerdefinierten Datenauszug auf allen\nDateien ausführen, die mit dem Scan-Pfad übereinstimmen,\ntesten Sie Ihren benutzerdefinierten Datenauszug\nan einer einzelnen, manuell ausgewählten Datei.\nÜberprüfen Sie, ob er die erwarteten Daten erhält\nund keine unerwarteten Nebenwirkungen hat.",
            'it': "Prima di eseguire la scansione e quindi eseguire l'estrazione dei dati personalizzati su tutti i\nfile che corrispondono al percorso di scansione,\ntestare l'estrattore di dati personalizzati\nsu un singolo file selezionato manualmente.\nVerificare se ottiene i dati previsti\ne se non ci sono effetti collaterali imprevisti.",
            'fr': "Avant d'exécuter le scan, et donc d'exécuter votre extracteur de données personnalisées sur tous\nles fichiers qui correspondent au chemin de scan,\ntestez votre extracteur de données personnalisées\nsur un seul fichier sélectionné manuellement.\nVérifiez s'il récupère les données attendues\net s'il n'y a pas d'effets secondaires inattendus.",
        },
        'TIMEOUT_TOOLTIP':{
            'en': "Timeout limit in seconds for single CD extraction.\nAfter timeout executed process will be terminated\n\n'0' or empty field means no timeout.",
            'pl': "Limit czasu w sekundach dla pojedynczej ekstrakcji CD.\nPo przekroczeniu limitu czasu wykonywany proces zostanie zakończony\n\n'0' lub puste pole oznacza brak limitu czasu.",
            'es': "Límite de tiempo en segundos para la extracción de un solo CD.\nDespués de que se ejecute el tiempo de espera, el proceso se terminará\n\n'0' o un campo vacío significa sin límite de tiempo.",
            'ru': "Предел времени в секундах для одиночной извлечения CD.\nПосле превышения времени выполнения процесс будет завершен\n\n'0' или пустое поле означает отсутствие ограничения по времени.",
            'de': "Zeitüberschreitungsgrenze in Sekunden für die einzelne CD-Extraktion.\nNach der Überschreitung der Zeit wird der Prozess beendet\n\n'0' oder ein leeres Feld bedeutet keine Zeitüberschreitung.",
            'it': "Limite di tempo in secondi per l'estrazione di un singolo CD.\nDopo il timeout, il processo verrà terminato\n\n'0' o un campo vuoto significa senza limite di tempo.",
            'fr': "Limite de temps en secondes pour l'extraction d'un seul CD.\nAprès l'expiration du délai, le processus sera terminé\n\n'0' ou un champ vide signifie pas de délai.",
        },
        'TIME_TOOLTIP':{
            'en': 'Date and time in the format below.\nLeave the value blank to ignore this criterion.\n\nexamples:\n2023-12-14 22:21:20\n2023-12-14 22:21\n2023-12-14\n2023-12',
            'pl': 'Data i godzina w poniższym formacie.\nPozostaw wartość pustą, aby zignorować to kryterium.\n\nPrzykłady:\n2023-12-14 22:21:20\n2023-12-14 22:21\n2023-12-14\n2023-12',
            'es': 'Fecha y hora en el formato a continuación.\nDeje el valor en blanco para ignorar este criterio.\n\nEjemplos:\n2023-12-14 22:21:20\n2023-12-14 22:21\n2023-12-14\n2023-12',
            'ru': 'Дата и время в формате ниже.\nОставьте значение пустым, чтобы проигнорировать этот критерий.\n\nПримеры:\n2023-12-14 22:21:20\n2023-12-14 22:21\n2023-12-14\n2023-12',
            'de': 'Datum und Uhrzeit im unten stehenden Format.\nLassen Sie den Wert leer, um dieses Kriterium zu ignorieren.\n\nBeispiele:\n2023-12-14 22:21:20\n2023-12-14 22:21\n2023-12-14\n2023-12',
            'it': 'Data e ora nel formato sottostante.\nLascia il valore vuoto per ignorare questo criterio.\n\nEsempi:\n2023-12-14 22:21:20\n2023-12-14 22:21\n2023-12-14\n2023-12',
            'fr': 'Date et heure au format ci-dessous.\nLaissez la valeur vide pour ignorer ce critère.\n\nExemples:\n2023-12-14 22:21:20\n2023-12-14 22:21\n2023-12-14\n2023-12',
        },
        'Test Custom Data Extractor on selected file ?':{
            'pl': 'Przetestować Ekstraktor Danych Użytkownika na wybranym pliku ?',
            'es': '¿Probar el extractor de datos personalizados en el archivo seleccionado?',
            'ru': 'Протестировать извлекатель пользовательских данных на выбранном файле?',
            'de': 'Den benutzerdefinierten Datenauszug auf der ausgewählten Datei testen?',
            'it': 'Testare l\'estrattore di dati personalizzati sul file selezionato?',
            'fr': 'Tester l\'extracteur de données personnalisées sur le fichier sélectionné ?',
        },
        'Testing selected Custom Data Extractor':{
            'pl': 'Testowanie Ekstraktora Danych Użytkownika',
            'es': 'Probando el extractor de datos personalizados seleccionado',
            'ru': 'Тестирование выбранного извлекателя пользовательских данных',
            'de': 'Testen des ausgewählten benutzerdefinierten Datenauszugs',
            'it': 'Test dell\'estrattore di dati personalizzati selezionato',
            'fr': 'Test de l\'extracteur de données personnalisées sélectionné',
        },
        'Text Files':{
            'pl': 'Pliki tekstowe',
            'es': 'Archivos de texto',
            'ru': 'Текстовые файлы',
            'de': 'Textdateien',
            'it': 'File di testo',
            'fr': 'Fichiers texte',
        },
        'Threshold:':{
            'pl': 'Próg:',
            'es': 'Umbral:',
            'ru': 'Порог:',
            'de': 'Schwellenwert:',
            'it': 'Soglia:',
            'fr': 'Seuil :',
        },
        'Time':{
            'pl': 'Czas',
            'es': 'Tiempo',
            'ru': 'Время',
            'de': 'Zeit',
            'it': 'Tempo',
            'fr': 'Temps',
        },
        'Translations are made using AI\nIf any corrections are necessary,\nplease contact the author.':{
            'pl': 'Tłumaczenia wykonane są przy użyciu AI.\nJeśli konieczne są jakiekolwiek poprawki, prosimy o kontakt z autorem.',
            'es': 'Las traducciones se realizan utilizando IA.\nSi se necesitan correcciones,\ncontacte con el autor.',
            'ru': 'Переводы выполнены с использованием ИИ.\nЕсли необходимы исправления,\nпожалуйста, свяжитесь с автором.',
            'de': 'Übersetzungen wurden mit KI erstellt.\nWenn Korrekturen erforderlich sind,\nwenden Sie sich bitte an den Autor.',
            'it': 'Le traduzioni sono effettuate con l\'AI.\nSe sono necessarie correzioni,\ncontattare l\'autore.',
            'fr': 'Les traductions sont effectuées à l\'aide de l\'IA.\nSi des corrections sont nécessaires,\nveuillez contacter l\'auteur.',
        },
        'UP_TOOLTIP':{
            'en': 'Use the arrow to change the order\nin which CDE criteria are checked.\n\nIf a file meets several CDE criteria\n(mask & size), the one with higher priority\nwill be executed. In this table, the first\none from the top has the highest priority,\nthe next ones have lower and lower priority.',
            'pl': 'Użyj strzałki, aby zmienić kolejność\nsprawdzania kryteriów CDE.\n\nJeśli plik spełnia kilka kryteriów CDE\n(maska \u200b\u200bi rozmiar), ten o wyższym priorytecie\nzostanie wykonany. W tej tabeli pierwszy\nplik od góry ma najwyższy priorytet,\nkolejne mają coraz niższy priorytet.',
            'es': 'Use la flecha para cambiar el orden\nen el que se verifican los criterios de CDE.\n\nSi un archivo cumple con varios criterios de CDE\n(máscara y tamaño), el de mayor prioridad\nserá ejecutado. En esta tabla, el primero\ndesde arriba tiene la mayor prioridad,\nlos siguientes tienen menor prioridad.',
            'ru': 'Используйте стрелку, чтобы изменить порядок\nпроверки критериев CDE.\n\nЕсли файл соответствует нескольким критериям CDE\n(маска и размер), тот, который имеет более высокий приоритет,\nбудет выполнен. В этой таблице первый\nсверху имеет наивысший приоритет,\nследующие имеют все более низкий приоритет.',
            'de': 'Verwenden Sie den Pfeil, um die Reihenfolge\nzu ändern, in der die CDE-Kriterien überprüft werden.\n\nWenn eine Datei mehrere CDE-Kriterien erfüllt\n(Maske und Größe), wird das mit höherer Priorität\nausgeführt. In dieser Tabelle hat die erste\nvon oben die höchste Priorität,\ndie nächsten haben immer geringere Prioritäten.',
            'it': 'Usa la freccia per cambiare l\'ordine\nin cui i criteri CDE vengono verificati.\n\nSe un file soddisfa più criteri CDE\n(maschera e dimensione), quello con priorità maggiore\nverrà eseguito. In questa tabella, il primo\nin alto ha la priorità più alta,\nquelli successivi hanno priorità sempre minore.',
            'fr': 'Utilisez la flèche pour modifier l\'ordre\nselon lequel les critères CDE sont vérifiés.\n\nSi un fichier satisfait plusieurs critères CDE\n(masque et taille), celui avec la priorité la plus élevée\nsera exécuté. Dans ce tableau, le premier\nen haut a la priorité la plus élevée,\nles suivants ont une priorité de plus en plus basse.',
        },
        'Unload record data':{
            'pl': 'Odładuj dane rekordu',
            'es': 'Descargar datos del registro',
            'ru': 'Загрузить данные записи',
            'de': 'Datensatzdaten entladen',
            'it': 'Scarica i dati del record',
            'fr': 'Décharger les données d\'enregistrement',
        },
        'Where Is It ? Import Records':{
            'pl': 'Where Is It ? importuj recordy',
            'es': '¿Dónde está? Importar registros',
            'ru': 'Где это? Импортировать записи',
            'de': 'Wo ist es? Datensätze importieren',
            'it': 'Dove si trova? Importa record',
            'fr': 'Où est-ce ? Importer des enregistrements',
        },
        'Where Is It? Import failed':{
            'pl': 'Import z Where Is It? Nie powiódł się',
            'es': '¿Dónde está? La importación falló',
            'ru': 'Где это? Ошибка импорта',
            'de': 'Wo ist es? Import fehlgeschlagen',
            'it': 'Dove si trova? Importazione fallita',
            'fr': 'Où est-ce ? Échec de l\'importation',
        },
        'Wrong executable':{
            'pl': 'Błędny plik wykonywalny',
            'es': 'Ejecutable incorrecto',
            'ru': 'Неверный исполнимый файл',
            'de': 'Falsche ausführbare Datei',
            'it': 'File eseguibile errato',
            'fr': 'Exécutable incorrect',
        },
        'Wrong mask expression':{
            'pl': 'Błędne wyrażenie maski',
            'es': 'Expresión de máscara incorrecta',
            'ru': 'Неверное выражение маски',
            'de': 'Falsche Maskenausdruck',
            'it': 'Espressione della maschera errata',
            'fr': 'Expression de masque incorrecte',
        },
        'XML Files':{
            'pl': 'Pliki XML',
            'es': 'Archivos XML',
            'ru': 'XML файлы',
            'de': 'XML-Dateien',
            'it': 'File XML',
            'fr': 'Fichiers XML',
        },
        'Yes':{
            'pl': 'Tak',
            'es': 'Sí',
            'ru': 'Да',
            'de': 'Ja',
            'it': 'Sì',
            'fr': 'Oui',
        },
        'based on the entire Custom Data of a file.':{
            'pl': 'na podstawie całości Danych Użytkownika pliku.',
            'es': 'basado en los datos completos del usuario de un archivo.',
            'ru': 'на основе всех данных пользователя файла.',
            'de': 'basierend auf den gesamten Benutzerdaten einer Datei.',
            'it': 'basato su tutti i dati utente di un file.',
            'fr': 'basé sur l\'ensemble des données utilisateur d\'un fichier.',
        },
        'based on the file or folder name.':{
            'pl': 'na podstawie nazwy pliku lub folderu.',
            'es': 'basado en el nombre del archivo o carpeta.',
            'ru': 'на основе имени файла или папки.',
            'de': 'basierend auf dem Dateinamen oder Ordnernamen.',
            'it': 'basato sul nome del file o della cartella.',
            'fr': 'basé sur le nom du fichier ou du dossier.',
        },
        'empty expression':{
            'pl': 'wyrażenie błędne',
            'es': 'expresión vacía',
            'ru': 'пустое выражение',
            'de': 'leerer Ausdruck',
            'it': 'espressione vuota',
            'fr': 'expression vide',
        },
        'for path element':{
            'pl': 'dla elementu ścieżki',
            'es': 'para el elemento de la ruta',
            'ru': 'для элемента пути',
            'de': 'für Pfadelement',
            'it': 'per elemento del percorso',
            'fr': 'pour l\'élément de chemin',
        },
        'found':{
            'pl': 'Znaleziono',
            'es': 'Encontrado',
            'ru': 'Найдено',
            'de': 'Gefunden',
            'it': 'Trovato',
            'fr': 'Trouvé',
        },
        'fuzzy expression error':{
            'pl': 'błąd wyrażenia rozmytego',
            'es': 'error de expresión difusa',
            'ru': 'ошибка размытое выражение',
            'de': 'fuzzy Ausdruck Fehler',
            'it': 'errore di espressione fuzzy',
            'fr': 'erreur d\'expression floue',
        },
        'fuzzy threshold error':{
            'pl': 'błąd wartości progu dopasowania rozmytego',
            'es': 'error de umbral difuso',
            'ru': 'ошибка порогового значения для нечеткого совпадения',
            'de': 'fuzzy Schwellenwert Fehler',
            'it': 'errore di soglia fuzzy',
            'fr': 'erreur de seuil flou',
        },
        'glob expression empty':{
            'pl': 'wyrażenie "glob" puste',
            'es': 'expresión glob vacía',
            'ru': 'пустое выражение glob',
            'de': 'glob Ausdruck leer',
            'it': 'espressione glob vuota',
            'fr': 'expression glob vide',
        },
        'group': {
            'pl': 'grupa',
            'es': 'grupo',
            'ru': 'группа',
            'de': 'Gruppe',
            'it': 'gruppo',
            'fr': 'groupe'
        },
        'group:': {
            'pl': 'grupa:',
            'es': 'grupo:',
            'ru': 'группа:',
            'de': 'Gruppe:',
            'it': 'gruppo:',
            'fr': 'groupe:'
        },
        'group: ': {
            'pl': 'grupa: ',
            'es': 'grupo: ',
            'ru': 'группа: ',
            'de': 'Gruppe: ',
            'it': 'gruppo: ',
            'fr': 'groupe: '
        },
        'index of the selected search result / search results total': {
            'pl': 'indeks wybranego wyniku wyszukiwania / całkowita liczba wyników wyszukiwania',
            'es': 'índice del resultado de búsqueda seleccionado / total de resultados de búsqueda',
            'ru': 'индекс выбранного результата поиска / общее количество результатов поиска',
            'de': 'Index des ausgewählten Suchergebnisses / Gesamtzahl der Suchergebnisse',
            'it': 'indice del risultato di ricerca selezionato / totale dei risultati di ricerca',
            'fr': 'indice du résultat de recherche sélectionné / total des résultats de recherche'
        },
        'items': {
            'pl': 'obiektów',
            'es': 'elementos',
            'ru': 'элементов',
            'de': 'Elemente',
            'it': 'elementi',
            'fr': 'éléments'
        },
        'loading Custom Data ...': {
            'pl': 'ładowanie Danych Użytkownika ...',
            'es': 'cargando Datos del Usuario ...',
            'ru': 'загрузка данных пользователя ...',
            'de': 'Benutzerdaten werden geladen ...',
            'it': 'caricamento Dati dell\'Utente ...',
            'fr': 'chargement des Données Utilisateur ...'
        },
        'loading filestructure ...': {
            'pl': 'ładowanie struktury plików ...',
            'es': 'cargando la estructura de archivos ...',
            'ru': 'загрузка структуры файлов ...',
            'de': 'Laden der Dateistruktur ...',
            'it': 'caricamento della struttura dei file ...',
            'fr': 'chargement de la structure des fichiers ...'
        },
        'max size value error': {
            'pl': 'błąd wartości wielkość max',
            'es': 'error en el valor de tamaño máximo',
            'ru': 'ошибка значения максимального размера',
            'de': 'Fehler im Wert für die maximale Größe',
            'it': 'errore nel valore della dimensione massima',
            'fr': 'erreur de valeur de taille maximale'
        },
        'min size value error': {
            'pl': 'błąd wartości wielkość min',
            'es': 'error en el valor de tamaño mínimo',
            'ru': 'ошибка значения минимального размера',
            'de': 'Fehler im Wert für die minimale Größe',
            'it': 'errore nel valore della dimensione minima',
            'fr': 'erreur de valeur de taille minimale'
        },
        'one device mode': {
            'pl': 'tryb pojedynczego urządzenia',
            'es': 'modo de un solo dispositivo',
            'ru': 'режим одного устройства',
            'de': 'Einzelgerätemodus',
            'it': 'modalità dispositivo singolo',
            'fr': 'mode un seul appareil'
        },
        'record:': {
            'pl': 'rekord:',
            'es': 'registro:',
            'ru': 'запись:',
            'de': 'Datensatz:',
            'it': 'record:',
            'fr': 'enregistrement:'
        },
        'regular expression empty': {
            'pl': 'wyrażenie regularne puste',
            'es': 'expresión regular vacía',
            'ru': 'пустое регулярное выражение',
            'de': 'leerer regulärer Ausdruck',
            'it': 'espressione regolare vuota',
            'fr': 'expression régulière vide'
        },
        'regular expression error': {
            'pl': 'błąd wyrażenia regularnego',
            'es': 'error en la expresión regular',
            'ru': 'ошибка регулярного выражения',
            'de': 'Fehler im regulären Ausdruck',
            'it': 'errore nell\'espressione regolare',
            'fr': 'erreur d\'expression régulière'
        },
        'rename': {
            'pl': 'nowa nazwa',
            'es': 'renombrar',
            'ru': 'переименовать',
            'de': 'umbenennen',
            'it': 'rinominare',
            'fr': 'renommer'
        },
        'scan path': {
            'pl': 'ścieżka skanowania',
            'es': 'ruta de escaneo',
            'ru': 'путь сканирования',
            'de': 'Scan-Pfad',
            'it': 'percorso di scansione',
            'fr': 'chemin de numérisation'
        },
        'subpath': {
            'pl': 'podścieżka',
            'es': 'subruta',
            'ru': 'подпуть',
            'de': 'Unterpfad',
            'it': 'sotto-percorso',
            'fr': 'sous-chemin'
        },
        'to group:': {
            'pl': 'do grupy:',
            'es': 'al grupo:',
            'ru': 'в группу:',
            'de': 'zur Gruppe:',
            'it': 'al gruppo:',
            'fr': 'au groupe:'
        },
        'with Error': {
            'pl': 'błędem',
            'es': 'con error',
            'ru': 'с ошибкой',
            'de': 'mit Fehler',
            'it': 'con errore',
            'fr': 'avec erreur'
        },
        'wrong threshold value': {
            'pl': 'błędna wartość progu',
            'es': 'valor de umbral incorrecto',
            'ru': 'неправильное значение порога',
            'de': 'falscher Schwellenwert',
            'it': 'valore di soglia errato',
            'fr': 'valeur de seuil incorrecte'
        },
        'Case sensitive': {
            'pl': 'Uwzględnij wielkość znaków',
            'es': 'Distinguir entre mayúsculas y minúsculas',
            'ru': 'Учитывать регистр',
            'de': 'Groß- und Kleinschreibung beachten',
            'it': 'Rispetta le maiuscole e minuscole',
            'fr': 'Respecter la casse'
        },
        'Checked on the entire Custom Data of a file.': {
            'pl': 'Sprawdzane na Danych Użytkownika pliku.',
            'es': 'Comprobado en los Datos de Usuario de un archivo.',
            'ru': 'Проверено по данным пользователя файла.',
            'de': 'Überprüft auf den Benutzerdefinierten Daten einer Datei.',
            'it': 'Controllato sui Dati Utente di un file.',
            'fr': 'Vérifié sur les Données Utilisateur d’un fichier.'
        },
        'Empty executable nr': {
            'pl': 'Pusty plik wykonywalny nr',
            'es': 'Archivo ejecutable vacío núm.',
            'ru': 'Пустой исполняемый файл №',
            'de': 'Leere ausführbare Datei Nr.',
            'it': 'File eseguibile vuoto n.',
            'fr': 'Fichier exécutable vide n°'
        },
        'Empty mask nr': {
            'pl': 'Pusta ścieżka nr',
            'es': 'Máscara vacía núm.',
            'ru': 'Пустая маска №',
            'de': 'Leere Maske Nr.',
            'it': 'Maschera vuota n.',
            'fr': 'Masque vide n°'
        },
        'Error on CD extraction': {
            'pl': 'Błąd na ekstrakcji Danych Użytkownika',
            'es': 'Error en la extracción de Datos de Usuario',
            'ru': 'Ошибка при извлечении данных пользователя',
            'de': 'Fehler bei der CD-Extraktion',
            'it': 'Errore nell\'estrazione dei Dati Utente',
            'fr': 'Erreur lors de l\'extraction des Données Utilisateur'
        },
        'Executable': {
            'pl': 'Plik wykonywalny',
            'es': 'Archivo ejecutable',
            'ru': 'Исполняемый файл',
            'de': 'Ausführbare Datei',
            'it': 'File eseguibile',
            'fr': 'Fichier exécutable'
        },
        'Executable Files': {
            'pl': 'Pliki Wykonywalne',
            'es': 'Archivos Ejecutables',
            'ru': 'Исполняемые файлы',
            'de': 'Ausführbare Dateien',
            'it': 'File eseguibili',
            'fr': 'Fichiers exécutables'
        },
        'Exit': {
            'pl': 'Zamknij',
            'es': 'Salir',
            'ru': 'Выход',
            'de': 'Beenden',
            'it': 'Esci',
            'fr': 'Quitter'
        },
        'Export': {
            'pl': 'Eksport',
            'es': 'Exportar',
            'ru': 'Экспорт',
            'de': 'Exportieren',
            'it': 'Esporta',
            'fr': 'Exporter'
        },
        'Export failed': {
            'pl': 'Eksport nie powiódł się',
            'es': 'Error en la exportación',
            'ru': 'Ошибка экспорта',
            'de': 'Export fehlgeschlagen',
            'it': 'Esportazione fallita',
            'fr': 'Échec de l\'exportation'
        },
        'Export record ...': {
            'pl': 'Eksportuj rekord',
            'es': 'Exportar registro ...',
            'ru': 'Экспортировать запись ...',
            'de': 'Datensatz exportieren ...',
            'it': 'Esporta record ...',
            'fr': 'Exporter l\'enregistrement ...'
        },
        'Extracted Custom Data: ': {
            'pl': 'Wyekstraktowane Dane Użytkownika: ',
            'es': 'Datos de usuario extraídos: ',
            'ru': 'Извлеченные данные пользователя: ',
            'de': 'Extrahierte Benutzerdaten: ',
            'it': 'Dati utente estratti: ',
            'fr': 'Données Utilisateur extraites : '
        },
        'Extraction Errors : ': {
            'pl': 'Błędy Ekstrakcji : ',
            'es': 'Errores de extracción : ',
            'ru': 'Ошибки извлечения : ',
            'de': 'Extraktionsfehler : ',
            'it': 'Errori di estrazione : ',
            'fr': 'Erreurs d\'extraction : '
        },
        'FUZZY_TOOLTIP': {
            'en': 'Fuzzy matching is implemented using SequenceMatcher\nfrom the difflib module. Any file whose similarity\nscore exceeds the threshold will be classified as found.\nThe similarity score is calculated\n',
            'pl': 'Dopasowanie rozmyte jest implementowane przy użyciu SequenceMatcher\nz modułu difflib. Każdy plik, którego podobieństwo\nwynik przekracza próg, zostanie sklasyfikowany jako znaleziony.\nWynik podobieństwa jest obliczany\n',
            'es': 'El emparejamiento difuso se implementa utilizando SequenceMatcher\ndel módulo difflib. Cualquier archivo cuya similitud\npuntuación supere el umbral se clasificará como encontrado.\nLa puntuación de similitud se calcula\n',
            'ru': 'Размытие сопоставления реализуется с использованием SequenceMatcher\nиз модуля difflib. Любой файл, чье сходство\nбалл превышает порог, будет классифицирован как найденный.\nСкорость сходства рассчитывается\n',
            'de': 'Fuzzy-Matching wird mit SequenceMatcher\naus dem difflib-Modul implementiert. Jede Datei, deren Ähnlichkeit\nPunktzahl den Schwellenwert überschreitet, wird als gefunden eingestuft.\nDer Ähnlichkeitswert wird berechnet\n',
            'it': 'Il matching fuzzy è implementato utilizzando SequenceMatcher\ndal modulo difflib. Qualsiasi file la cui similarità\npunteggio supera la soglia verrà classificato come trovato.\nIl punteggio di similarità viene calcolato\n',
            'fr': 'Le rapprochement flou est implémenté en utilisant SequenceMatcher\ndu module difflib. Tout fichier dont le score de similarité\nexcède le seuil sera classé comme trouvé.\nLe score de similarité est calculé\n'
        },
        'File': {
            'pl': 'Plik',
            'es': 'Archivo',
            'ru': 'Файл',
            'de': 'Datei',
            'it': 'File',
            'fr': 'Fichier'
        },
        'File Mask': {
            'pl': 'Maska Plików',
            'es': 'Máscara de archivo',
            'ru': 'Маска файла',
            'de': 'Dateimaske',
            'it': 'Maschera file',
            'fr': 'Masque de fichier'
        },
        'File last modification time': {
            'pl': 'Ostatni czas modyfikacji pliku',
            'es': 'Última hora de modificación del archivo',
            'ru': 'Время последней модификации файла',
            'de': 'Letzte Änderungszeit der Datei',
            'it': 'Ultimo orario di modifica del file',
            'fr': 'Dernière modification du fichier'
        },
        'File size': {
            'pl': 'Wielkość pliku',
            'es': 'Tamaño del archivo',
            'ru': 'Размер файла',
            'de': 'Dateigröße',
            'it': 'Dimensione del file',
            'fr': 'Taille du fichier'
        },
        'Files with aborted CD extraction': {
            'pl': 'Pliki z błędem podczas ekstrakcji Danych Użytkownika',
            'es': 'Archivos con extracción de Datos de Usuario abortada',
            'ru': 'Файлы с ошибкой при извлечении данных пользователя',
            'de': 'Dateien mit abgebrochener CD-Extraktion',
            'it': 'File con estrazione dei Dati Utente interrotta',
            'fr': 'Fichiers avec extraction des Données Utilisateur interrompue'
        },
        'Files with any correct Custom Data': {
            'pl': 'Pliki z jakimikolwiek poprawnymi Danymi Użytkownika',
            'es': 'Archivos con cualquier dato de usuario correcto',
            'ru': 'Файлы с любыми правильными данными пользователя',
            'de': 'Dateien mit beliebigen korrekten Benutzerdaten',
            'it': 'File con dati utente corretti',
            'fr': 'Fichiers avec des Données Utilisateur correctes'
        },
        'Files with empty CD value': {
            'pl': 'Pliki z pustymi Danymi Użytkownika',
            'es': 'Archivos con datos de usuario vacíos',
            'ru': 'Файлы с пустыми данными пользователя',
            'de': 'Dateien mit leeren Benutzerdaten',
            'it': 'File con dati utente vuoti',
            'fr': 'Fichiers avec des Données Utilisateur vides'
        },
        'Files with error on CD extraction': {
            'pl': 'Pliki z błędem na ekstrakcji Danych Użytkownika',
            'es': 'Archivos con error en la extracción de Datos de Usuario',
            'ru': 'Файлы с ошибкой при извлечении данных пользователя',
            'de': 'Dateien mit Fehler bei der CD-Extraktion',
            'it': 'File con errore nell\'estrazione dei Dati Utente',
            'fr': 'Fichiers avec erreur lors de l\'extraction des Données Utilisateur'
        },
        'Files without Custom Data': {
            'pl': 'Pliki bez Danych Użytkownika',
            'es': 'Archivos sin Datos de Usuario',
            'ru': 'Файлы без данных пользователя',
            'de': 'Dateien ohne Benutzerdaten',
            'it': 'File senza Dati Utente',
            'fr': 'Fichiers sans Données Utilisateur'
        },
        'Find ...': {
            'pl': 'Szukaj',
            'es': 'Buscar ...',
            'ru': 'Найти ...',
            'de': 'Suchen ...',
            'it': 'Trova ...',
            'fr': 'Rechercher ...'
        },
        'Find next': {
            'pl': 'Znajdź następny',
            'es': 'Buscar siguiente',
            'ru': 'Найти следующий',
            'de': 'Nächste finden',
            'it': 'Trova successivo',
            'fr': 'Trouver suivant'
        },
        'Find prev': {
            'pl': 'Znajdź poprzedni',
            'es': 'Buscar anterior',
            'ru': 'Найти предыдущий',
            'de': 'Vorheriges finden',
            'it': 'Trova precedente',
            'fr': 'Trouver précédent'
        },
        'Found Files': {
            'pl': 'Znaleziono plików',
            'es': 'Archivos encontrados',
            'ru': 'Найдено файлов',
            'de': 'Gefundene Dateien',
            'it': 'File trovati',
            'fr': 'Fichiers trouvés'
        },
        'Full path copied to clipboard': {
            'pl': 'Pełna ścieżka skopiowana do schowka',
            'es': 'Ruta completa copiada al portapapeles',
            'ru': 'Полный путь скопирован в буфер обмена',
            'de': 'Vollständiger Pfad in die Zwischenablage kopiert',
            'it': 'Percorso completo copiato negli appunti',
            'fr': 'Chemin complet copié dans le presse-papiers'
        },
        'Fuzzy match on Custom Data': {
            'pl': 'Dopasowanie rozmyte na Danych Użytkownika',
            'es': 'Coincidencia difusa en los Datos de Usuario',
            'ru': 'Размытие сопоставления на данных пользователя',
            'de': 'Fuzzy-Matching auf Benutzerdaten',
            'it': 'Matching fuzzy sui Dati Utente',
            'fr': 'Correspondance floue sur les Données Utilisateur'
        },
        'Fuzzy match on path element': {
            'pl': 'Dopasowanie rozmyte na elemencie ścieżki',
            'es': 'Coincidencia difusa en el elemento de la ruta',
            'ru': 'Размытие сопоставления на элементе пути',
            'de': 'Fuzzy-Matching auf Pfadelement',
            'it': 'Matching fuzzy su elemento del percorso',
            'fr': 'Correspondance floue sur l\'élément du chemin'
        }
    }

    def __init__(self):
        pass

    def set(self,lang_id):
        self.lang_id=lang_id

    def STR(self,str_par,new_lang=None):
        try:
            return self.STR_DICT[str_par][self.lang_dict[new_lang if new_lang else self.lang_id]]
        except:
            try:
                return self.STR_DICT[str_par]["en"]
            except:
                return str_par

