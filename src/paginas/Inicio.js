import React from 'react';
import escudo from '../assets/img/computadora1.png';

export const Inicio = () => {
    return(
        <div>
            <h1>Inicio</h1>
            <img src={escudo} alt="escudo" height={300} width={400}/>
        </div>
    )
}