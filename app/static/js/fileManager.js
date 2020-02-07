function FileManager () {
  this.cat = {
    "bread": [],
    "filelist": []
  }
  this.breadUl = document.getElementById('breads')
  this.treeUl = document.getElementById('tree')
  this.fileName = document.getElementById('fileName')
  this.loaderBlock = document.getElementById('loader')
  this.dataFile = $('#dataFile')
  this.loader = function (status) {
    this.loaderBlock.style.display = status ? 'flex' : 'none'
  }
}
FileManager.prototype.openFolder = function (obj, type = 'folder', name) {
  if (type === 'file') {
    this.loader(true)
    this.fileName.innerText = obj.replace(/\|/g, '/')
  }
  $.ajax( {
    url: `${host}/api/v1/open${type}/${obj ? obj : ''}`,
    type: 'GET',
    crossDomain: true,
    dataType: 'json',
    success: ( data ) => {
      if (type === 'folder'){
        this.cat = data
        this.generateList()
      }else{
        if ($.fn.DataTable.isDataTable( '#dataFile' ) ) {
          this.dataFile.fnDestroy()
        }
        this.dataFile.dataTable({
          data: data.data,
          columns: data.header.map(el => ({
            title: el
          }))
        })
      }
    },
    complete: () => {
      this.loader(false)
    }
  })
}
FileManager.prototype.generateList = function () {
  this.breadUl.innerHTML = ''
  this.treeUl.innerHTML = ''
  this.cat.bread.forEach((bread, index) => {
    const breadLi = document.createElement('li')
    breadLi.addEventListener('click', this.openFolder.bind(this, bread.folderfullname, 'folder', ''))
    breadLi.innerText = bread.foldername + ((index && index !== this.cat.bread.length - 1) ? '/' : '')
    this.breadUl.appendChild(breadLi)
  })
  this.cat.filelist.forEach((tree, index) => {
    const treeLi = document.createElement('li')
    
    const icon = document.createElement('i')
    icon.classList.add('material-icons')
    icon.innerText = tree.type === 'file' ? 'insert_drive_file' : 'folder'
    
    const name = document.createElement('span')
    name.innerText = tree.filename
    
    
    // treeLi.onclick = function () {
    //   console.log(this)
    //   this.openFolder(tree.fullfilename, tree.type, tree.filename)
    // }
    treeLi.addEventListener('click', this.openFolder.bind(this, tree.fullfilename, tree.type, tree.filename))
    treeLi.appendChild(icon)
    treeLi.appendChild(name)
    if (tree.type === 'file') {
      const size = document.createElement('span')
      size.classList.add('size')
      size.innerText = `${tree.size} Б`
      treeLi.appendChild(size)
    }
    this.treeUl.appendChild(treeLi)
  })
}
