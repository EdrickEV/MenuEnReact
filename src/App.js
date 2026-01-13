import './App.css';
import { Route, Routes, BrowserRouter } from 'react-router-dom';
import Navbar from './componentes/Navbar';
import Bienvenida from './paginas/Bienvenidas';
import { Inicio } from './paginas/Inicio';
import Contacto from './paginas/Contacto';
import Destacados from './paginas/Destacados';
import Informaciones from './paginas/Informaciones';
import escudo from './assets/img/cecytem.png';

function App() {
  return(
    <div className='App'>
      <img src={escudo} alt="escudo" height={50} width={80}/>
      <h1>CECYTEM, plantel Tenango del Valle</h1>
      <div style={{ borderBottom: '1px solid #ccc', margin: '10px 0' }}></div>

      <BrowserRouter>
          <Navbar/>
            <Routes>
              <Route path='/' element={<Bienvenida/>}/>
              <Route path='/inicio' element={<Inicio/>}/>
              <Route path='/contacto' element={<Contacto/>}/>
              <Route path='/destacados' element={<Destacados/>}/>
              <Route path='/informaciones' element={<Informaciones/>}/>
            </Routes>
      </BrowserRouter>

    </div>
  );
}


export default App;