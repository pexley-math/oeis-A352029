#set page(
  paper: "a4",
  margin: (top: 2cm, bottom: 2cm, left: 1.5cm, right: 1.5cm),
  header: context {
    if counter(page).get().first() > 1 [
      #align(center)[#text(size: 8pt, fill: luma(120))[A352029: Number of Minimalist Polyomino Containers]]
    ]
  },
  footer: context {
    let current = counter(page).get().first()
    let total = counter(page).final().first()
    align(center)[#text(size: 8pt, fill: luma(120))[Page #current of #total]]
  },
)
#set text(font: "New Computer Modern", size: 9pt)

#align(center)[
  #text(size: 16pt, weight: "bold")[A352029: Number of Minimalist Polyomino Containers]
  #v(0.3em)
  #text(size: 10pt)[a(n) = number of distinct free polyominoes of minimum size A327094(n) containing all free n-ominoes]
  #v(0.2em)
  #text(size: 10pt)[1, 1, 2, 2, 2, 14, 204, 7]
  #v(0.2em)
  #text(size: 8pt, style: "italic")[Computed by Peter Exley, April 2026]
]
#v(0.5em)
#line(length: 100%, stroke: 0.5pt)
#v(0.3em)
#block(breakable: false, width: 100%)[
#align(center)[
  #text(size: 11pt, weight: "bold")[$a(8) = 20$]#text(size: 8pt, fill: rgb("#27AE60"), weight: "bold")[ \[PROVED\]]
  #h(0.5em)
  #text(size: 8pt)[Solution 1/7, 4 x 8 bounding box]
]
#v(0.2em)
#align(center)[
#table(
  columns: (7mm,) * 8,
  rows: (7mm,) * 4,
  inset: 0pt,
  stroke: 0.5pt + white,
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
)
]
]
#v(0.5em)
#block(breakable: false, width: 100%)[
#align(center)[
  #text(size: 11pt, weight: "bold")[$a(8) = 20$]#text(size: 8pt, fill: rgb("#27AE60"), weight: "bold")[ \[PROVED\]]
  #h(0.5em)
  #text(size: 8pt)[Solution 2/7, 4 x 8 bounding box]
]
#v(0.2em)
#align(center)[
#table(
  columns: (7mm,) * 8,
  rows: (7mm,) * 4,
  inset: 0pt,
  stroke: 0.5pt + white,
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
)
]
]
#v(0.5em)
#block(breakable: false, width: 100%)[
#align(center)[
  #text(size: 11pt, weight: "bold")[$a(8) = 20$]#text(size: 8pt, fill: rgb("#27AE60"), weight: "bold")[ \[PROVED\]]
  #h(0.5em)
  #text(size: 8pt)[Solution 3/7, 4 x 8 bounding box]
]
#v(0.2em)
#align(center)[
#table(
  columns: (7mm,) * 8,
  rows: (7mm,) * 4,
  inset: 0pt,
  stroke: 0.5pt + white,
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
)
]
]
#v(0.5em)
#block(breakable: false, width: 100%)[
#align(center)[
  #text(size: 11pt, weight: "bold")[$a(8) = 20$]#text(size: 8pt, fill: rgb("#27AE60"), weight: "bold")[ \[PROVED\]]
  #h(0.5em)
  #text(size: 8pt)[Solution 4/7, 4 x 8 bounding box]
]
#v(0.2em)
#align(center)[
#table(
  columns: (7mm,) * 8,
  rows: (7mm,) * 4,
  inset: 0pt,
  stroke: 0.5pt + white,
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
)
]
]
#v(0.5em)
#block(breakable: false, width: 100%)[
#align(center)[
  #text(size: 11pt, weight: "bold")[$a(8) = 20$]#text(size: 8pt, fill: rgb("#27AE60"), weight: "bold")[ \[PROVED\]]
  #h(0.5em)
  #text(size: 8pt)[Solution 5/7, 4 x 8 bounding box]
]
#v(0.2em)
#align(center)[
#table(
  columns: (7mm,) * 8,
  rows: (7mm,) * 4,
  inset: 0pt,
  stroke: 0.5pt + white,
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
)
]
]
#v(0.5em)
#block(breakable: false, width: 100%)[
#align(center)[
  #text(size: 11pt, weight: "bold")[$a(8) = 20$]#text(size: 8pt, fill: rgb("#27AE60"), weight: "bold")[ \[PROVED\]]
  #h(0.5em)
  #text(size: 8pt)[Solution 6/7, 8 x 5 bounding box]
]
#v(0.2em)
#align(center)[
#table(
  columns: (7mm,) * 5,
  rows: (7mm,) * 8,
  inset: 0pt,
  stroke: 0.5pt + white,
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
)
]
]
#v(0.5em)
#block(breakable: false, width: 100%)[
#align(center)[
  #text(size: 11pt, weight: "bold")[$a(8) = 20$]#text(size: 8pt, fill: rgb("#27AE60"), weight: "bold")[ \[PROVED\]]
  #h(0.5em)
  #text(size: 8pt)[Solution 7/7, 4 x 8 bounding box]
]
#v(0.2em)
#align(center)[
#table(
  columns: (7mm,) * 8,
  rows: (7mm,) * 4,
  inset: 0pt,
  stroke: 0.5pt + white,
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: rgb("#4A90D9"))[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
  table.cell(fill: white)[],
)
]
]
