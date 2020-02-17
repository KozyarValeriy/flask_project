/*
    Автор: Горшков Павел
*/

function FileManager () {
  this.cat = {
    bread: [],
    filelist: [],
  }
  this.fileInfo = {
    fullfilename: '',
    size: 0,
    paginate: {
      query: '',
      countLines: 100,
      startByte: 0,
      stopByte: 0
    }
  }
  this.breadUl = document.getElementById('breads')
  this.treeUl = document.getElementById('tree')
  this.fileName = document.getElementById('fileName')
  this.loaderBlock = document.getElementById('loader')
  this.paginateBlock = document.getElementById('paginateFile')
  this.dataFile = null
  this.loader = function (status) {
    this.loaderBlock.style.display = status ? 'flex' : 'none'
  }
  this.setActiveFile = function (path) {
    path.parentNode.querySelectorAll('li').forEach(el => {
      if (el === path) {
        if(!path.classList.contains('active')){
          path.classList.add('active')
          this.fileInfo = {
            fullfilename: '',
            size: 0,
            paginate: {
              query: '',
              countLines: 100,
              startByte: 0,
              stopByte: 0
            }
          }
        }
      } else {
        el.classList.remove('active')
      }
    })
  }
}
FileManager.prototype.openFolder = function (obj) {
  $.ajax( {
    url: `${host}/api/v1/openfolder/${obj ? obj : ''}`,
    type: 'GET',
    crossDomain: true,
    dataType: 'json',
    success: ( data ) => {
      this.cat = data
      this.generateList()
    },
    complete: () => {
      this.loader(false)
    }
  })
}
FileManager.prototype.openFile = function (obj, step, event) {
  this.setActiveFile(event.path[1])
  const data = {}
  this.loader(true)
  this.fileName.innerText = obj.fullfilename.replace(/\|/g, '/')
  data.countLines = this.fileInfo.paginate.countLines
  if (event.toElement.id !== 'search') {
    data.startByte = (step === 'next') ? this.fileInfo.paginate.stopByte : this.fileInfo.paginate.startByte
  } else {
    data.startByte = this.fileInfo.paginate.startByte
  }
  data.step = step
  if (document.getElementById('query') && document.getElementById('query').value) {
    data.query = this.fileInfo.paginate.query = document.getElementById('query').value
  }
  $.ajax( {
    url: `${host}/api/v1/openfile/${obj.fullfilename}`,
    type: 'GET',
    data,
    crossDomain: true,
    dataType: 'json',
    success: ( data ) => {
      this.fileInfo = { ...this.fileInfo,
        fullfilename: obj.fullfilename,
        size: obj.size,
        paginate: {
          ...this.fileInfo.paginate,
          startByte: data.startByte,
          stopByte: data.stopByte
        }
      }
      if ($.fn.DataTable.isDataTable( '#dataFile' ) ) {
        this.dataFile.api().destroy()
        $('#dataFile').empty()
      }
      this.dataFile = $('#dataFile').dataTable({
        paging: false,
        bInfo: false,
        data: data.data,
        columns: data.header.map(el => ({
          title: el
        }))
      })
      this.paginateInfo()
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
    breadLi.addEventListener('click', this.openFolder.bind(this, bread.folderfullname, 'folder'))
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
    if (tree.type === 'file') {
      if (this.fileInfo.fullfilename !== tree.fullfilename){
        treeLi.addEventListener('click', this.openFile.bind(this, tree, 'next'))
      }
    } else {
      treeLi.addEventListener('click', this.openFolder.bind(this, tree.fullfilename))
    }
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

FileManager.prototype.paginateInfo = function () {
  this.paginateBlock.style.display = 'flex'
  this.paginateBlock.innerText = ''
  
  const btnPrev = document.createElement('button')
  btnPrev.innerText = '<<<'
  if (this.fileInfo.paginate.startByte === 0){
    btnPrev.setAttribute('disabled', 'disabled')
  }
  btnPrev.addEventListener('click', this.openFile.bind(this, this.fileInfo, 'prev'))
  this.paginateBlock.appendChild(btnPrev)
  
  const infoPath = document.createElement('span')
  infoPath.innerText = 'от ' + this.fileInfo.paginate.startByte + 'Б до ' + this.fileInfo.paginate.stopByte + 'Б из ' + this.fileInfo.size + 'Б'
  this.paginateBlock.appendChild(infoPath)
  
  const btnNext = document.createElement('button')
  btnNext.innerText = '>>>'
  if (this.fileInfo.paginate.stopByte === this.fileInfo.size){
    btnNext.setAttribute('disabled', 'disabled')
  }
  btnNext.addEventListener('click', this.openFile.bind(this, this.fileInfo, 'next'))
  this.paginateBlock.appendChild(btnNext)
  
  const query = document.createElement('input')
  query.setAttribute('id', 'query')
  query.setAttribute('value', this.fileInfo.paginate.query)
  query.setAttribute('placeholder', 'Query')
  this.paginateBlock.appendChild(query)
  
  const btnSearch = document.createElement('button')
  btnSearch.innerText = 'Поиск'
  btnSearch.setAttribute('id', 'search')
  btnSearch.addEventListener('click', this.openFile.bind(this, this.fileInfo, 'next'))
  this.paginateBlock.appendChild(btnSearch)
}
