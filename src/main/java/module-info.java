module com.mycompany.ui_for_python {
    requires javafx.controls;
    requires javafx.fxml;

    opens com.mycompany.ui_for_python to javafx.fxml;
    exports com.mycompany.ui_for_python;
}
