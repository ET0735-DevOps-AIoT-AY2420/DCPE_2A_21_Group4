function activeTab(selectedTab) {
    
    const menuItems = document.querySelectorAll('.menu-item');

    
    menuItems.forEach((item) => {
        item.classList.remove('active'); 
    });

   
    selectedTab.classList.add('active'); 
}
