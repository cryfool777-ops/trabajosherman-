using System;
using System.Collections.Generic;

public class ListaEnlazada
{
    private readonly List<int> datos = new List<int>();

    public void RecorridoSecuencial()
    {
        Console.WriteLine("Recorrido secuencial: " + string.Join(" ", datos));
    }

    public void RecorridoInverso()
    {
        List<int> inverso = new List<int>(datos);
        inverso.Reverse();
        Console.WriteLine("Recorrido inverso: " + string.Join(" ", inverso));
    }

    public void InsertarAlInicio(int valor) => datos.Insert(0, valor);

    public void InsertarAlFinal(int valor) => datos.Add(valor);

    public bool EliminarAlInicio()
    {
        if (datos.Count == 0) return false;
        datos.RemoveAt(0);
        return true;
    }

    public bool EliminarAlFinal()
    {
        if (datos.Count == 0) return false;
        datos.RemoveAt(datos.Count - 1);
        return true;
    }

    public bool EliminarElegida(int indice)
    {
        if (indice < 0 || indice >= datos.Count) return false;
        datos.RemoveAt(indice);
        return true;
    }

    public int BusquedaSecuencial(int valor)
    {
        for (int i = 0; i < datos.Count; i++)
            if (datos[i] == valor) return i;
        return -1;
    }

    public int BusquedaBinaria(int valor)
    {
        int izquierda = 0, derecha = datos.Count - 1;
        while (izquierda <= derecha)
        {
            int medio = izquierda + (derecha - izquierda) / 2;
            if (datos[medio] == valor) return medio;
            if (datos[medio] < valor) izquierda = medio + 1;
            else derecha = medio - 1;
        }
        return -1;
    }

    public void Ordenar() => datos.Sort();

    public static void Main()
    {
        ListaEnlazada lista = new ListaEnlazada();
        lista.InsertarAlFinal(30);
        lista.InsertarAlFinal(10);
        lista.InsertarAlFinal(20);
        lista.InsertarAlInicio(5);
        lista.RecorridoSecuencial();
        lista.RecorridoInverso();
        lista.EliminarAlInicio();
        lista.EliminarAlFinal();
        lista.EliminarElegida(0);
        lista.InsertarAlFinal(40);
        lista.InsertarAlFinal(20);
        lista.InsertarAlFinal(10);
        lista.Ordenar();
        lista.RecorridoSecuencial();
        Console.WriteLine("Busqueda secuencial de 20: indice " + lista.BusquedaSecuencial(20));
        Console.WriteLine("Busqueda binaria de 20: indice " + lista.BusquedaBinaria(20));
    }
}

