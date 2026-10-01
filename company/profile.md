# Tanmark Industries: company profile

**Tanmark Industries is a fictional company. It was built to show the shape of a real system; it contains no
real client or employer data.** Every number about it comes from a synthetic dataset and is labelled illustrative.
The design patterns in the case study are real ones from order-processing and accounting systems.

## What it does

Tanmark builds steel products to order in three workshops: truck-mounted tanks and vehicle bodies, steel drums, and
containers. It sells them to about sixty business customers, and it also sells services: repair and maintenance of the
vehicles and tanks it built.

## The ten departments

1. Director's office (the director is the executive sponsor)
2. Product sales (sells what the workshops build)
3. Technical management (engineering, production planning and quality)
4. Production, in three workshops:
   * the vehicle workshop, for truck-mounted tanks and vehicle bodies
   * the drum workshop
   * the container workshop
5. Warehouse (materials and finished goods)
6. Logistics and purchasing (logistics coordinators plan fulfilment and delivery; buyers order materials)
7. Price control (checks sale and purchase prices against the price list)
8. Service sales (sells repair and maintenance contracts)
9. Accounting
10. Human resources

Logistics and purchasing is a department of its own here, apart from sales, so that each handoff in the case study is
a handoff between departments.

## The team that built the system

* A **product owner**, who owns the requirements, the backlog and its order, the roadmap and the rollout.
* A **team of six developers**: a tech lead, four engineers and a security engineer.
* An **executive sponsor**, the director, who reviews the roadmap every week and decides go or no-go for each phase.

## The processes in scope

1. **Order to cash.** Sales saves an order request and confirms it into an order, then hands it to logistics.
   Logistics fulfils it from stock or raises a material request; a workshop builds the goods; the warehouse receives
   finished goods and issues them to a delivery trip; accounting raises the trip's invoice, and the trip leaves with it.
   Customers are businesses that buy on credit: each pays on its contract's terms, usually 30 days, and accounting
   allocates the receipts and chases what is overdue.
2. **Procure to pay.** A buyer creates a purchase order, signed on paper; the warehouse receives the materials into
   stock; accounting records the supplier's invoice and posts the payment.
3. **Accounting.** Every receipt and payment is a voucher that is saved, then posted; a posted voucher never changes.

## Before

Orders arrived by phone and email and were written on paper forms. Stock lived in spreadsheets that no one trusted,
and logistics checked it by walking the shelves. Purchases were emailed to suppliers and noted in a spreadsheet.
Invoices were keyed into the accounting tool by hand, and payments matched to them by hand. Payment terms sat in a
binder, so overdue customers were found only when the quarter-end statements went out. Nobody could see where an order
was stuck.

## After

One back-office system on one data model, in linked applications for sales and logistics, stock and production, and
accounting. Every document has a lifecycle with named states (see `state/state-model.md`), each person's access follows
their role, and a transition table says who may move each document.

## Role boundary

**Purchasing, accounting and sales policy remain the business's functions.** The product owner decides what the system
does and in what order it is built and rolled out. Buyers decide what to buy and from whom, price control checks the
price, and the logistics manager signs purchase orders. Finance decides posting and correction policy and what to pay.
The sales and logistics leads decide how an order may close. The case study shows the system enforcing those
decisions, never making them.

The boundary held in both directions. When warehouse keepers asked to check the stock form before issuing or
receiving, a step the product owner had not designed, that control was theirs to decide; the product owner built it,
and kept the form's official number tied to the stock movement (D15).
