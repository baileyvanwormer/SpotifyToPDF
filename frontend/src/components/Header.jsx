// src/components/Header.jsx
const Header = () => {
    return (
      <header className="site-header">
        <div class="dropdown">
            <button onclick="myFunction()" class="dropbtn">Dropdown</button>
            <div id="myDropdown" class="dropdown-content">
                <a href="#">Link 1</a>
                <a href="#">Link 2</a>
                <a href="#">Link 3</a>
            </div>
        </div>
        <h2>ExportMyMusic.com</h2>
      </header>
    );
  };
  
  export default Header;
  