1. Notwendige Pakete in der Python Umgebung installieren (z.b. Keras. Dies kann über die Installation vonTesorflow erfolgen)
2. Docker installieren
3. In Docker unter Settings/Resources/File Sharing den Dateipfad zum Programmcode hinzufügen
4. Docker Container erstellen. Hierzu:
    - Console öffnen (cmd.exe)
    - folgenden Befehl eingeben
        docker run -p 8501:8501 --name tool_classifier --mount type=bind,source=/classifier/tool_classifier/,target=/models/tool_classifier -e MODEL_NAME=tool_classifier -t tensorflow/serving

    - nach der Erstellung des Containers kann dieser über die Benutzeroberfläche von Docker verwaltet werden.