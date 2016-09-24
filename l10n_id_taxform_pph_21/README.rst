.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================================================
Indonesia's PPh 21 Taxform Related Configuration and Computation
================================================================

This module provide configurations and computation that related to
Indonesia's income tax article 21.

Available configurations:

1. Penghasilan Tidak Kena Pajak (PTKP)
2. Biaya Jabatan
3. PPh 21 NPWP Rate Modifier
4. PPh 21 Rate for objek pajak 21-100-01 and 21-100-02

Available computation:

1. PPh 21 for objek pajak 21-100-01 and 21-100-02

All the computations will be used by another modules that needed the
computations.

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/l10n-indonesia
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Indonesia's PPh 21 Taxform Related Configuration and Computation*
6.  Install the module


Usage
=====

**PTKP Categories**

To manage PTKP categories, you need to:

1. Go to menu *Taxform -> Configuration -> PPh 21 -> PTKP Category*

**PTKP Rates**

To manage PTKP rates, you need to:

1. Go to menu *Taxform -> Configuration -> PPh 21 -> PTKP Rates*

**Biaya Jabatan**

To manage Biaya Jabatan, you need to:

1. Go to menu *Taxform -> Configuration -> PPh 21 -> Biaya Jabatan*

**Non-NPWP Rate Modifiers**

To manage Non-NPWP Rate Modifiers, you need to:

1. Go to menu *Taxform -> Configuration -> PPh 21 -> Non-NPWP Rate Modifiers*

**PPh 21 Rates**

To manage PPh 21 Rates, you need to:

1. Go to menu *Taxform -> Configuration -> PPh 21 -> PPh 21 Rates*

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/219/8.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/l10n-indonesia/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
