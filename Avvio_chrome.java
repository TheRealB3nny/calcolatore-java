import javax.swing.*;
import java.awt.*;
import java.io.IOException;

public class Avvio_chrome {
    public static void main(String[] args) {
        JFrame frame = new JFrame("Apri Chrome");
        JButton button = new JButton("Apri Chrome");

        button.addActionListener(e -> {
            String chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
            try {
                ProcessBuilder processBuilder = new ProcessBuilder(chromePath);
                processBuilder.start();
            } catch (IOException ex) {
                JOptionPane.showMessageDialog(frame, "Errore: impossibile aprire Chrome.\nVerifica il percorso.", "Errore", JOptionPane.ERROR_MESSAGE);
            }
        });

        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(300, 200);
        frame.setLayout(new FlowLayout()); // Migliora il layout
        frame.add(button);
        frame.setLocationRelativeTo(null); // Centra la finestra
        frame.setVisible(true);
    }
}
