package com.mycompany.ui_for_python;

import java.io.*;
import java.net.URL;
import java.util.ResourceBundle;

import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Accordion;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.Menu;
import javafx.scene.control.MenuItem;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TextArea;
import javafx.scene.control.TreeView;
import javafx.scene.input.MouseEvent;
import javafx.scene.control.TitledPane;
import javafx.scene.control.TreeCell;
import javafx.scene.control.TreeItem;
import javafx.stage.DirectoryChooser;
import java.util.List;

public class PrimaryController implements Initializable {

    File selectedDirectory;
    
    @FXML
    private Menu archivos_Recientes;

    @FXML
    private MenuItem abrir_Archivo;

    @FXML
    private MenuItem abrir_Carpeta;

    @FXML
    private MenuItem aserca_de;

    @FXML
    private MenuItem cerrar_Archivo;

    @FXML
    private MenuItem cerrar_Carpeta;

    @FXML
    private MenuItem copiar;

    @FXML
    private MenuItem cortar;

    @FXML
    private MenuItem desceleccionar_Todo;

    @FXML
    private MenuItem deshacer;

    @FXML
    private MenuItem eliminar;

    @FXML
    private MenuItem guardar_Archivo;

    @FXML
    private MenuItem guardar_Archivo_Como;

    @FXML
    private MenuItem nuevo_Archivo;

    @FXML
    private MenuItem pegar;

    @FXML
    private MenuItem preferencesias;

    @FXML
    private MenuItem rehacer;

    @FXML
    private MenuItem salir;

    @FXML
    private MenuItem selecionar_Todo;

    @FXML
    private Button arbol;

    @FXML
    private Button pause;

    @FXML
    private Button play;

    @FXML
    private TextArea salida;

    @FXML
    private Label status;

    @FXML
    private Accordion acordeon;
    
    @FXML
    private TreeView<File> file_Explorer;

    @FXML
    private TabPane tab_panel;
    
    @Override
    public void initialize(URL arg0, ResourceBundle arg1) {
        
    }

    public void seleecionar_carpeta() {
        DirectoryChooser directoryChooser = new DirectoryChooser();
        directoryChooser.setTitle("Selecciona una carpeta");

        selectedDirectory = directoryChooser.showDialog(pause.getScene().getWindow());

        if (selectedDirectory != null) {
            String[] pach_folder_splited = selectedDirectory.getAbsolutePath().split("\\\\");
            String name_folder = pach_folder_splited[pach_folder_splited.length-1];
            
            TreeItem<File> rootItem = new TreeItem<>(selectedDirectory);
            rootItem.setExpanded(true);
            addFilesToTreeItem(selectedDirectory, rootItem);

            file_Explorer.setRoot(rootItem);
            file_Explorer.setShowRoot(false);
            TitledPane tPanel = new TitledPane(name_folder,file_Explorer);
            acordeon.getPanes().clear();
            acordeon.getPanes().add(tPanel);
            // tPanel.
        } else {
            System.out.println("No se seleccionó ninguna carpeta.");
        }
        file_Explorer.setCellFactory(tv -> new TreeCell<File>() {
            @Override
            protected void updateItem(File file, boolean empty) {
                super.updateItem(file, empty);
                if (empty) {
                    setText(null);
                } else {
                    setText(file.getName()); // Mostrar solo el nombre del archivo/carpeta
                }
            }
        });
        file_Explorer.addEventHandler(MouseEvent.MOUSE_CLICKED, event -> {
            TreeItem<File> selectedItem = file_Explorer.getSelectionModel().getSelectedItem();
            if (selectedItem != null && selectedItem.getValue().isFile()) {
                openFileInNewTab(selectedItem.getValue());
            }
        });
    }

    private void openFileInNewTab(File file) {
        // Comprobar si el archivo ya está abierto en una pestaña
        for (Tab tab : tab_panel.getTabs()) {
            if (tab.getText().equals(file.getName())) {
                tab_panel.getSelectionModel().select(tab); // Seleccionar la pestaña si ya está abierta
                return;
            }
        }

        // Crear un TextArea para editar el contenido del archivo
        TextArea textArea = new TextArea();
        textArea.setWrapText(true);

        // Leer el contenido del archivo y mostrarlo en el TextArea
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            StringBuilder content = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line).append("\n");
            }
            textArea.setText(content.toString());
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Crear una nueva pestaña
        Tab tab = new Tab(file.getName(), textArea);

        // Agregar un listener para guardar los cambios cuando se cierra la pestaña
        tab.setOnCloseRequest(event -> {
            saveFile(file, textArea.getText());
        });

        // Agregar la pestaña al tab_panel y seleccionarla
        tab_panel.getTabs().add(tab);
        tab_panel.getSelectionModel().select(tab);
    }

    private void saveFile(File file, String content) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(file))) {
            writer.write(content);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void ejecutarPythonScript() {
        // Obtener el archivo de la pestaña actualmente seleccionada
        Tab selectedTab = tab_panel.getSelectionModel().getSelectedItem();
        if (selectedTab == null) {
            salida.setText("No hay pestaña seleccionada.");
            return;
        }

        // Obtener el nombre del archivo desde la pestaña
        String archivoActual = selectedTab.getText();

        // Ruta del script de Python que deseas ejecutar
        String pythonScript = "src/main/java/Python/Lexer.py"; // Cambiar por la ruta correcta del script Python

        // Ruta del archivo en la pestaña activa
        String rutaArchivoEnTab = "ruta/completa/al/archivo/"; // Cambiar por la ruta completa del archivo activo

        for (File file : selectedDirectory.listFiles()) {
            String name_file = file.getName();
            if (name_file.compareTo(archivoActual) == 0) {
                rutaArchivoEnTab = file.getAbsolutePath().toString();
                break;
            }
        }
        
        // Crear un comando para ejecutar el script Python
        List<String> comando = List.of(
                "python",      // Comando para ejecutar Python
                pythonScript,  // Ruta del script de Python
                "-f",          // Opción que deseas pasar
                rutaArchivoEnTab // Ruta del archivo que está en el TabPanel
        );

        try {
            // Crear el proceso
            ProcessBuilder processBuilder = new ProcessBuilder(comando);
            processBuilder.redirectErrorStream(true); // Combinar stdout y stderr

            // Ejecutar el proceso
            Process process = processBuilder.start();

            // Leer la salida del proceso
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }

            // Mostrar la salida en el Label
            salida.setText(output.toString());

        } catch (Exception e) {
            // Mostrar cualquier error en la ejecución
            salida.setText("Error al ejecutar el script: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void addFilesToTreeItem(File directory, TreeItem<File> parentItem) {
        File[] files = directory.listFiles(); // Obtener el contenido de la carpeta

        if (files != null) {
            for (File file : files) {
                // Crear un nuevo TreeItem para cada archivo o carpeta
                TreeItem<File> fileItem = new TreeItem<>(file);

                // Si es un directorio, agregar su contenido recursivamente
                if (file.isDirectory()) {
                    addFilesToTreeItem(file, fileItem);
                }

                // Agregar el TreeItem al elemento padre
                parentItem.getChildren().add(fileItem);
            }
        }
    }
}
