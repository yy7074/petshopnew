import 'package:get/get.dart';
import '../pages/splash/splash_page.dart';
import '../pages/auth/login_page.dart';
import '../pages/main/main_page.dart';
import '../pages/home/home_page.dart';
import '../pages/category/category_page.dart';
import '../pages/message/message_page.dart';
import '../pages/profile/profile_page.dart';
import '../pages/product/product_detail_page.dart';
import '../pages/search/search_page.dart';
import '../pages/test_payment_page.dart';
import '../pages/auction/auction_winner_order_page.dart';
import '../pages/auction/auction_test_page.dart';
import '../pages/wallet/wallet_page.dart';
import '../pages/store/store_page.dart';
import '../pages/bids/bid_records_page.dart';

class AppRoutes {
  static const String splash = '/splash';
  static const String login = '/login';
  static const String main = '/main';
  static const String home = '/home';
  static const String category = '/category';
  static const String message = '/message';
  static const String profile = '/profile';
  static const String productDetail = '/product-detail';
  static const String search = '/search';
  static const String testPayment = '/test-payment';
  static const String auctionWinnerOrder = '/auction-winner-order';
  static const String auctionTest = '/auction-test';
  static const String wallet = '/wallet';
  static const String store = '/store';
  static const String bidRecords = '/bid-records';

  static List<GetPage> routes = [
    GetPage(
      name: splash,
      page: () => const SplashPage(),
    ),
    GetPage(
      name: login,
      page: () => const LoginPage(),
    ),
    GetPage(
      name: main,
      page: () => const MainPage(),
    ),
    GetPage(
      name: home,
      page: () => const HomePage(),
    ),
    GetPage(
      name: category,
      page: () => const CategoryPage(),
    ),
    GetPage(
      name: message,
      page: () => const MessagePage(),
    ),
    GetPage(
      name: profile,
      page: () => const ProfilePage(),
    ),
    GetPage(
      name: productDetail,
      page: () => ProductDetailPage(
        productData: Get.arguments is Map<String, dynamic>
            ? Get.arguments as Map<String, dynamic>
            : null,
      ),
    ),
    GetPage(
      name: search,
      page: () => const SearchPage(),
    ),
    GetPage(
      name: testPayment,
      page: () => const TestPaymentPage(),
    ),
    GetPage(
      name: auctionWinnerOrder,
      page: () => const AuctionWinnerOrderPage(),
    ),
    GetPage(
      name: auctionTest,
      page: () => const AuctionTestPage(),
    ),
    GetPage(
      name: wallet,
      page: () => const WalletPage(),
    ),
    GetPage(
      name: store,
      page: () => StorePage(
        storeId: Get.arguments?['store_id'],
        sellerId: Get.arguments?['seller_id'],
      ),
    ),
    GetPage(
      name: bidRecords,
      page: () => const BidRecordsPage(),
    ),
  ];
}
