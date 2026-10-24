#include <algorithm>
#include <iostream>
#include <vector>

class Lista {
private:
    std::vector<int> datos;

public:
    void recorridoSecuencial() const {
        std::cout << "Recorrido secuencial: ";
        for (int valor : datos) std::cout << valor << ' ';
        std::cout << '\n';
    }

    void recorridoInverso() const {
        std::cout << "Recorrido inverso: ";
        for (auto iterador = datos.rbegin(); iterador != datos.rend(); ++iterador)
            std::cout << *iterador << ' ';
        std::cout << '\n';
    }

    void insertarAlInicio(int valor) { datos.insert(datos.begin(), valor); }
    void insertarAlFinal(int valor) { datos.push_back(valor); }

    bool eliminarAlInicio() {
        if (datos.empty()) return false;
        datos.erase(datos.begin());
        return true;
    }

    bool eliminarAlFinal() {
        if (datos.empty()) return false;
        datos.pop_back();
        return true;
    }

    bool eliminarElegida(std::size_t indice) {
        if (indice >= datos.size()) return false;
        datos.erase(datos.begin() + static_cast<long>(indice));
        return true;
    }

    int busquedaSecuencial(int valor) const {
        for (std::size_t i = 0; i < datos.size(); ++i)
            if (datos[i] == valor) return static_cast<int>(i);
        return -1;
    }

    int busquedaBinaria(int valor) const {
        int izquierda = 0;
        int derecha = static_cast<int>(datos.size()) - 1;
        while (izquierda <= derecha) {
            int medio = izquierda + (derecha - izquierda) / 2;
            if (datos[medio] == valor) return medio;
            if (datos[medio] < valor) izquierda = medio + 1;
            else derecha = medio - 1;
        }
        return -1;
    }

    void ordenar() { std::sort(datos.begin(), datos.end()); }
};

int main() {
    Lista lista;
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
    std::cout << "Busqueda secuencial de 20: indice " << lista.busquedaSecuencial(20) << '\n';
    std::cout << "Busqueda binaria de 20: indice " << lista.busquedaBinaria(20) << '\n';
}
