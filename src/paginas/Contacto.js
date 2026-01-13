import { useState,React } from 'react';

const Contacto = () => {
    const [nombre, setNombre] = useState('');
    const [email, setEmail] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault(); // Evitar que la pagina se recargue
        console.log('Formulario enviado:', {nombre, email });
        alert(`Hola ${nombre}, tu email es ${email}`);
    };
    return(
        <div>
            <h1>Contacto</h1><br />
            <from onSubmit={handleSubmit}>
                <div>
                    <label htmlFor='nombre'>Nombre:</label>
                    <input type="text" id="nombre" value={nombre} onChange={(e) => setNombre(e.target.value)}  />
                </div>
                <div>
                    <label htmlFor='nombre'>Email:</label>
                    <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)}  />
                </div>
                <button type="submit">Enviar</button>
            </from>
        </div>
    )
}

export default Contacto;