/** open the first contig information*/
document.addEventListener("DOMContentLoaded", function () {
  /** add event listener to table row */
  [].slice.call(document.querySelectorAll("#nanocap_summary tr"), 1).forEach(row => {
    const selectedClass = "is-selected";
    row.addEventListener("click", () => {
        /* get row informations */
        const ths = document.querySelectorAll("#nanocap_summary th", 1);
        const rowObj = [].reduce.call(ths, (acc, th, i) => {
            const { textContent } = row.cells[i];
            acc[th.textContent] = textContent;
            return acc;
        }, {});

        /* update row style */
        if (!row.classList.contains(selectedClass)) {
            var pastRow = document.getElementById('nanocap_summary').getElementsByClassName(selectedClass)[0];
            if (pastRow) {
                /* hide past row */
                pastRow.classList.remove(selectedClass);
                const pastRowObj = [].reduce.call(ths, (acc, th, i) => {
                    const { textContent } = pastRow.cells[i];
                    acc[th.textContent] = textContent;
                    return acc;
                }, {});
                document.getElementById(pastRowObj.Contig).style.display = "none";
            }
            row.classList.add(selectedClass);
            document.getElementById(rowObj.Contig).style.display = "block";
        }
    });
  });

  document.getElementById("defaultOpenAssembly").click();
})
