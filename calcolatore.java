import java.util.InputMismatchException;
import java.util.Scanner;

public class calcolatore {

    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        boolean continua = true;

        System.out.println("===========================");
        System.out.println("|   🎉CALCOLATORE🎉   |");
        System.out.println("===========================");

        while (continua) {
            mostraMenu();
            System.out.print("Scegli un'opzione: ");
            int operazione = leggiIntero(input);

            double numero1 = 0, numero2 = 0;
            if (operazione >= 1 && operazione <= 6) {
                numero1 = leggiDouble(input, "Inserisci il primo numero: ");
                numero2 = leggiDouble(input, "Inserisci il secondo numero: ");
            }

            switch (operazione) {
                case 1 -> stampaRisultato("Moltiplicazione", moltiplica(numero1, numero2));
                case 2 -> {
                    if (numero2 == 0) {
                        System.out.println("\u26a0 Errore: divisione per zero non consentita.");
                    } else {
                        stampaRisultato("Divisione", dividi(numero1, numero2));
                    }
                }
                case 3 -> stampaRisultato("Addizione", somma(numero1, numero2));
                case 4 -> stampaRisultato("Sottrazione", sottrai(numero1, numero2));
                case 5 -> calcolaQuadrato(input, numero1, numero2);
                case 6 -> calcolaMedia(input, numero1, numero2);
                case 7 -> calcolaRadice(input);
                case 8 -> stampaFibonacci(input);
                case 9 -> stampaTabellina(input);
                case 10 -> calcolaFattoriale(input);
                case 0 -> {
                    System.out.println("Grazie per aver utilizzato il calcolatore. \uD83D\uDE4F\uD83C\uDFFB Alla prossima!");
                    continua = false;
                }
                default -> System.out.println("\u26a0 Operazione non riconosciuta. Riprova.");
            }

            if (continua) {
                System.out.print("\nVuoi eseguire un'altra operazione? (s/n): ");
                String risposta = input.next();
                continua = risposta.equalsIgnoreCase("s");
            }
        }

        input.close();
    }

    static void mostraMenu() {
        System.out.println("\n===== Ecco a te il menù delle operazioni =====");
        System.out.println("1. Moltiplicazione");
        System.out.println("2. Divisione");
        System.out.println("3. Addizione");
        System.out.println("4. Sottrazione");
        System.out.println("5. Quadrato");
        System.out.println("6. Media");
        System.out.println("7. Radice quadrata");
        System.out.println("8. Serie di Fibonacci");
        System.out.println("9. Tabellina");
        System.out.println("10. Fattoriale");
        System.out.println("0. Esci");
    }

    static double leggiDouble(Scanner input, String messaggio) {
        while (true) {
            try {
                System.out.print(messaggio);
                return input.nextDouble();
            } catch (InputMismatchException e) {
                System.out.println("\u26a0 Inserisci un numero valido!");
                input.next();
            }
        }
    }

    static int leggiIntero(Scanner input) {
        while (true) {
            try {
                return input.nextInt();
            } catch (InputMismatchException e) {
                System.out.print("\u26a0 Inserisci un numero intero valido: ");
                input.next();
            }
        }
    }

    static void stampaRisultato(String operazione, double risultato) {
        System.out.println("Risultato della " + operazione + ": " + risultato);
    }

    static double moltiplica(double a, double b) {
        return a * b;
    }

    static double dividi(double a, double b) {
        return a / b;
    }

    static double somma(double a, double b) {
        return a + b;
    }

    static double sottrai(double a, double b) {
        return a - b;
    }

    static void calcolaQuadrato(Scanner input, double n1, double n2) {
        System.out.println("Quale numero vuoi elevare al quadrato? (1 o 2)");
        int scelta = leggiIntero(input);
        double risultato = (scelta == 1) ? Math.pow(n1, 2) : (scelta == 2) ? Math.pow(n2, 2) : -1;

        if (risultato != -1) {
            stampaRisultato("Quadrato", risultato);
        } else {
            System.out.println("Scelta non valida.");
        }
    }

    static void calcolaMedia(Scanner input, double n1, double n2) {
        System.out.println("Calcolare la media solo dei primi due numeri (1) o aggiungerne altri (2)?");
        int scelta = leggiIntero(input);

        if (scelta == 1) {
            stampaRisultato("Media", (n1 + n2) / 2);
        } else if (scelta == 2) {
            double n3 = leggiDouble(input, "Inserisci il terzo numero: ");
            double n4 = leggiDouble(input, "Inserisci il quarto numero: ");
            stampaRisultato("Media", (n1 + n2 + n3 + n4) / 4);
        } else {
            System.out.println("Scelta non valida.");
        }
    }

    static void calcolaRadice(Scanner input) {
        double n = leggiDouble(input, "Inserisci un numero per la radice quadrata: ");
        stampaRisultato("Radice quadrata", Math.sqrt(n));
    }

    static void stampaFibonacci(Scanner input) {
        System.out.print("Quanti numeri della serie Fibonacci vuoi visualizzare? ");
        int count = leggiIntero(input);
        if (count <= 0) {
            System.out.println("Numero non valido.");
            return;
        }
        long a = 0, b = 1;
        System.out.print("Serie: " + a);
        for (int i = 1; i < count; i++) {
            System.out.print(" " + b);
            long temp = b;
            b = a + b;
            a = temp;
        }
        System.out.println();
    }

    static void stampaTabellina(Scanner input) {
        int n = (int) leggiDouble(input, "Inserisci un numero positivo per la tabellina: ");
        if (n <= 0) {
            System.out.println("Numero non valido.");
            return;
        }
        for (int i = 1; i <= 10; i++) {
            System.out.printf("%d x %d = %d\n", n, i, n * i);
        }
    }

    static void calcolaFattoriale(Scanner input) {
        int n = (int) leggiDouble(input, "Inserisci un numero per il fattoriale: ");
        if (n < 0) {
            System.out.println("Il fattoriale non è definito per numeri negativi.");
            return;
        }
        long risultato = 1;
        for (int i = 2; i <= n; i++) {
            risultato *= i;
        }
        stampaRisultato("Fattoriale", risultato);
    }
}