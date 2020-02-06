// var host = 'http://77.244.211.197'
var host = ''

var cat = {
  "bread": [],
  "filelist": []
}
var breadUl = document.getElementById('breads')
var treeUl = document.getElementById('tree')
var fileName = document.getElementById('fileName')
$(function () {
  openFolder()
});


function openFolder (obj, type = 'folder', name = '') {
  $.ajax( {
    url: `${host}/api/v1/open${type}/${obj ? obj : ''}`,
    type: 'GET',
    crossDomain: true,
    dataType: 'json',
    success: function( data ) {
      if (type === 'folder'){
        cat = data
        generateList()
      }else{
      }
    }
  })
  
  fileName.innerText = (type === 'file') ? name : ''
}

function generateList () {
  breadUl.innerHTML = ''
  treeUl.innerHTML = ''
  cat.bread.forEach((bread, index) => {
    const breadLi = document.createElement('li')
    breadLi.onclick = function () {
      openFolder(bread.folderfullname)
    }
    breadLi.innerText = bread.foldername + ((index && index !== cat.bread.length - 1) ? '/' : '')
    breadUl.appendChild(breadLi)
  })
  cat.filelist.forEach((tree, index) => {
    const treeLi = document.createElement('li')
    
    const icon = document.createElement('i')
    icon.classList.add('material-icons')
    icon.innerText = tree.type === 'file' ? 'insert_drive_file' : 'folder'
    
    const name = document.createElement('span')
    name.innerText = tree.filename
    
    
    treeLi.onclick = function () {
      openFolder(tree.fullfilename, tree.type, tree.filename)
    }
    treeLi.appendChild(icon)
    treeLi.appendChild(name)
    if (tree.type === 'file') {
      const size = document.createElement('span')
      size.classList.add('size')
      size.innerText = `${tree.size} Б`
      treeLi.appendChild(size)
    }
    treeUl.appendChild(treeLi)
  })
}
