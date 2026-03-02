This module allows to define on a Product Package (stock.package), a
Product Packaging (uom.uom, listed in the product's packagings) if said
package only contains Quants (stock.quant) from this product, and the sum
of the quants quantities is equal to the packaging quantity.

If such a packaging exists, it will be automatically assigned to a
package after the move is set to done.

The module also computes the package type of the package when products are put in a package.
The computation is done based on the number of products in the package.
