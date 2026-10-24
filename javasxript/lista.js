class Lista {
  #datos = [];

  recorridoSecuencial() {
    console.log("Recorrido secuencial: [" + this.#datos.join(", ") + "]");
  }

  recorridoInverso() {
    const inverso = [...this.#datos].reverse();
    console.log("Recorrido inverso: [" + inverso.join(", ") + "]");
  }

  insertarAlInicio(valor) { this.#datos.unshift(valor); }
  insertarAlFinal(valor) { this.#datos.push(valor); }

  eliminarAlInicio() {
    if (this.#datos.length === 0) return false;
    this.#datos.shift();
    return true;
  }

  eliminarAlFinal() {
    if (this.#datos.length === 0) return false;
    this.#datos.pop();
    return true;
  }

  eliminarElegida(indice) {
    if (indice < 0 || indice >= this.#datos.length) return false;
    this.#datos.splice(indice, 1);
    return true;
  }

  busquedaSecuencial(valor) {
    for (let i = 0; i < this.#datos.length; i++) {
      if (this.#datos[i] === valor) return i;
    }
    return -1;
  }

  busquedaBinaria(valor) {
    let izquierda = 0;
    let derecha = this.#datos.length - 1;
    while (izquierda <= derecha) {
      const medio = izquierda + Math.floor((derecha - izquierda) / 2);
      if (this.#datos[medio] === valor) return medio;
      if (this.#datos[medio] < valor) izquierda = medio + 1;
      else derecha = medio - 1;
    }
    return -1;
  }

  ordenar() {
    this.#datos.sort((a, b) => a - b);
  }
}

// main
const lista = new Lista();
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
console.log("Busqueda secuencial de 20: indice " + lista.busquedaSecuencial(20));
console.log("Busqueda binaria de 20: indice " + lista.busquedaBinaria(20));