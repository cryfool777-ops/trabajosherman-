import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Lista {
    private final List<Integer> datos = new ArrayList<>();

    public void recorridoSecuencial() {
        System.out.println("Recorrido secuencial: " + datos);
    }

    public void recorridoInverso() {
        List<Integer> inverso = new ArrayList<>(datos);
        Collections.reverse(inverso);
        System.out.println("Recorrido inverso: " + inverso);
    }

    public void insertarAlInicio(int valor) { datos.add(0, valor); }
    public void insertarAlFinal(int valor) { datos.add(valor); }

    public boolean eliminarAlInicio() {
        if (datos.isEmpty()) return false;
        datos.remove(0);
        return true;
    }

    public boolean eliminarAlFinal() {
        if (datos.isEmpty()) return false;
        datos.remove(datos.size() - 1);
        return true;
    }

    public boolean eliminarElegida(int indice) {
        if (indice < 0 || indice >= datos.size()) return false;
        datos.remove(indice);
        return true;
    }

    public int busquedaSecuencial(int valor) {
        for (int i = 0; i < datos.size(); i++)
            if (datos.get(i) == valor) return i;
        return -1;
    }

    public int busquedaBinaria(int valor) {
        int izquierda = 0, derecha = datos.size() - 1;
        while (izquierda <= derecha) {
            int medio = izquierda + (derecha - izquierda) / 2;
            if (datos.get(medio) == valor) return medio;
            if (datos.get(medio) < valor) izquierda = medio + 1;
            else derecha = medio - 1;
        }
        return -1;
    }

    public void ordenar() { Collections.sort(datos); }

    public static void main(String[] args) {
        Lista lista = new Lista();
        lista.insertarAlFinal(30);
        lista.insertarAlFinal(10);
        lista.insertarAlFinal(20);
        lista.insertarAlInicio(5);
        lista.recorridoSecuencial();
        lista.recorridoInverso();
        lista.eliminarAlInicio();
        lista.eliminarAlFinal();
        lista.eliminarElegida(0);
        lista.insertarAlFinal(40);
        lista.insertarAlFinal(20);
        lista.insertarAlFinal(10);
        lista.ordenar();
        lista.recorridoSecuencial();
        System.out.println("Busqueda secuencial de 20: indice " + lista.busquedaSecuencial(20));
        System.out.println("Busqueda binaria de 20: indice " + lista.busquedaBinaria(20));
    }
}
