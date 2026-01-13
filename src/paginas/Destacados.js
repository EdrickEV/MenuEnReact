import React, { useState } from 'react';

const Destacados = () => {
    const [datos] = useState([
        { id: 1, nombre: 'Alice', edad: 30 },
        { id: 2, nombre: 'Bob', edad: 25 },
        { id: 3, nombre: 'Charlie', edad: 35 },
    ]);

    return(
        <div>Destacados
            <table>
                <thead>
                    <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Edad</th>
                    </tr>
                </thead>
                <tbody>
                    {datos.map((item) => (
                    <tr key={item.id}>
                        <td>{item.id}</td>
                        <td>{item.nombre}</td>
                        <td>{item.edad}</td>
                    </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default Destacados;